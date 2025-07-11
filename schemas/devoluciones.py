from pydantic import BaseModel
from typing import List
from datetime import datetime

class ItemDevolucion(BaseModel):
    producto_id: int
    cantidad: int

class DevolucionCreate(BaseModel):
    venta_id: int
    items: List[ItemDevolucion]

class DetalleDevolucionOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    descuento_individual: float
    subtotal: float

    class Config:
        orm_mode = True

class DevolucionOut(BaseModel):
    id: int
    venta_id: int
    fecha: datetime
    detalles: List[DetalleDevolucionOut]

    class Config:
        orm_mode = True
