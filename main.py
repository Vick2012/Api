from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models.reserva import ReservaCreate, ReservaDB
from app.database.connection import reservas_collection
from bson import ObjectId
from typing import List, Optional
from dotenv import load_dotenv
import os
from fastapi.staticfiles import StaticFiles 

# Inicializar FastAPI
app = FastAPI(title="Reservas Restaurante")

# Montar la carpeta 'static' para servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Cargar variables de entorno
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
if MONGO_URL is None:
    raise ValueError("La variable de entorno MONGO_URL no está configurada.")


# Configurar Jinja2 para plantillas
templates = Jinja2Templates(directory="templates")

# Manejo de errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detalle": exc.errors(), "cuerpo": exc.body},
    )

# Endpoint para la interfaz básica en HTML
@app.get("/", response_class=HTMLResponse)
async def interfaz_reservas(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint para crear una nueva reserva
@app.post("/reservas/", response_model=ReservaDB, status_code=status.HTTP_201_CREATED)
async def crear_reserva(reserva: ReservaCreate):
    try:
        print("Intentando crear una nueva reserva...")
        reserva_dict = reserva.dict()
        print("Datos recibidos:", reserva_dict)
        resultado = await reservas_collection.insert_one(reserva_dict)
        print("Registro insertado, ID:", resultado.inserted_id)
        nueva_reserva = await reservas_collection.find_one({"_id": resultado.inserted_id})
        print("Reserva encontrada:", nueva_reserva)
        nueva_reserva["id"] = str(nueva_reserva["_id"])
        del nueva_reserva["_id"]
        return ReservaDB(**nueva_reserva)
    except Exception as e:
        print("Error al insertar en MongoDB:", str(e))
        raise HTTPException(status_code=500, detail=f"Error interno al guardar la reserva: {str(e)}")

# Endpoint para listar todas las reservas con búsqueda opcional
@app.get("/reservas/", response_model=List[ReservaDB])
async def listar_reservas(search: Optional[str] = None):
    try:
        print("Intentando listar reservas...")
        reservas = []
        query = {}
        if search:
            # Filtrar por nombre, teléfono o email usando una expresión regular
            search_regex = {"$regex": search, "$options": "i"}  # "i" para case-insensitive
            query = {
                "$or": [
                    {"nombre_cliente": search_regex},
                    {"telefono": search_regex},
                    {"email": search_regex}
                ]
            }
        async for reserva in reservas_collection.find(query):
            print("Reserva encontrada:", reserva)
            reserva["id"] = str(reserva["_id"])
            del reserva["_id"]
            reservas.append(ReservaDB(**reserva))
        print("Total de reservas encontradas:", len(reservas))
        return reservas
    except Exception as e:
        print("Error al listar reservas:", str(e))
        raise HTTPException(status_code=500, detail=f"Error al listar reservas: {str(e)}")

# Endpoint para obtener una reserva por ID
@app.get("/reservas/{reserva_id}", response_model=ReservaDB)
async def obtener_reserva(reserva_id: str):
    if not ObjectId.is_valid(reserva_id):
        raise HTTPException(status_code=400, detail="ID de reserva inválido")
    reserva = await reservas_collection.find_one({"_id": ObjectId(reserva_id)})
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    reserva["id"] = str(reserva["_id"])
    del reserva["_id"]
    return ReservaDB(**reserva)

# Endpoint para actualizar una reserva
@app.put("/reservas/{reserva_id}", response_model=ReservaDB)
async def actualizar_reserva(reserva_id: str, reserva_update: ReservaCreate):
    if not ObjectId.is_valid(reserva_id):
        raise HTTPException(status_code=400, detail="ID de reserva inválido")
    update_data = reserva_update.dict(exclude_unset=True)
    if len(update_data) == 0:
        raise HTTPException(status_code=400, detail="Datos de actualización vacíos")
    result = await reservas_collection.update_one(
        {"_id": ObjectId(reserva_id)},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    reserva_actualizada = await reservas_collection.find_one({"_id": ObjectId(reserva_id)})
    reserva_actualizada["id"] = str(reserva_actualizada["_id"])
    del reserva_actualizada["_id"]
    return ReservaDB(**reserva_actualizada)

# Endpoint para eliminar una reserva
@app.delete("/reservas/{reserva_id}")
async def eliminar_reserva(reserva_id: str):
    if not ObjectId.is_valid(reserva_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    result = await reservas_collection.delete_one({"_id": ObjectId(reserva_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return {"mensaje": "Reserva eliminada"}

# Endpoint para verificar la conexión a MongoDB
@app.get("/ping")
async def ping():
    try:
        await reservas_collection.database.command("ping")
        return {"message": "Conexión exitosa a MongoDB!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar a MongoDB: {str(e)}")