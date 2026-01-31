from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime

# Solo para entrada (crear devolución) → no necesita from_attributes
class ItemDevolucion(BaseModel):
    producto_id: int
    cantidad: int

class DevolucionCreate(BaseModel):
    venta_id: int
    items: List[ItemDevolucion]
    reponer_stock: bool = True
    detalle: str | None = None

# Modelos que devuelven datos (respuesta) → sí necesitan from_attributes
class DetalleDevolucionOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    descuento_individual: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)

class DevolucionOut(BaseModel):
    id: int
    venta_id: int
    fecha: datetime
    reponer_stock: bool
    detalle: str | None
    detalles: List[DetalleDevolucionOut]

    model_config = ConfigDict(from_attributes=True)
