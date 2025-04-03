from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

# Verificar si la URL de MongoDB se ha cargado correctamente
if MONGO_URL is None:
    raise ValueError("La variable de entorno MONGO_URL no está configurada.")

# Conectar con MongoDB usando AsyncIOMotorClient
client = AsyncIOMotorClient(MONGO_URL)
db = client.Reserva  # Cambia 'Reserva' por el nombre de tu base de datos
reservas_collection = db.reserva_restaurante  # Cambia 'reserva_restaurante' por el nombre de tu colección

# Crear la aplicación FastAPI
app = FastAPI()

# Endpoint de prueba para verificar la conexión
@app.get("/ping")
async def ping():
    try:
        await client.admin.command('ping')
        return {"message": "Conexión exitosa a MongoDB!"}
    except Exception as e:
        return {"error": str(e)}