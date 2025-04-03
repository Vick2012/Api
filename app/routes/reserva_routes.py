from fastapi import status
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.reserva import Reserva
from app.database.connection import reservas_collection as collection
from bson import ObjectId
from bson.errors import InvalidId

router = APIRouter()


@router.post("/", response_model=Reserva, status_code=201)
async def crear_reserva(reserva: Reserva):
    nueva_reserva = reserva.dict()
    result = await collection.insert_one(nueva_reserva)
    nueva_reserva["_id"] = str(result.inserted_id)
    return nueva_reserva

@router.get("/{id}", response_model=Reserva)  
async def obtener_reserva(id: str):  
    try:
        obj_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID no válido")

    reserva = await collection.find_one({"_id": obj_id})
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    reserva["_id"] = str(reserva["_id"])
    return reserva

@router.get("/", response_model=List[Reserva])  
async def obtener_reservas():
    reservas = await collection.find().to_list(100)
    for reserva in reservas:
        reserva["_id"] = str(reserva["_id"])
    return reservas

@router.put("/{id}", response_model=Reserva)
async def actualizar_reserva(id: str, reserva: Reserva):
    try:
        obj_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID no válido")

    result = await collection.update_one({"_id": obj_id}, {"$set": reserva.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    return {**reserva.dict(), "_id": id}

@router.delete("/eliminar-por-nombre/{nombre_cliente}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_reserva_por_nombre(nombre_cliente: str):
    # Buscar y eliminar la reserva por nombre_cliente
    result = await collection.delete_one({"nombre_cliente": nombre_cliente})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No se encontró ninguna reserva con ese nombre.")