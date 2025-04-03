from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class ReservaCreate(BaseModel):
    nombre_cliente: str = Field(..., min_length=3, max_length=50)
    fecha_reserva: datetime
    numero_personas: int = Field(..., ge=1, le=20)  # Cambiar gt=0 por ge=1
    telefono: str = Field(..., min_length=10, max_length=15)
    email: EmailStr

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class ReservaDB(ReservaCreate):
    id: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}