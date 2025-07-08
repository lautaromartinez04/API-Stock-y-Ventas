from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DetalleVentaCreate(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float

class VentaBase(BaseModel):
    cliente_id: Optional[int]
    usuario_id: int

class VentaCreate(VentaBase):
    detalles: List[DetalleVentaCreate]
    descuento: Optional[float] = Field(
        0.0, ge=0, le=100, description="Porcentaje de descuento (0–100)"
    )

class Venta(VentaBase):
    id: int
    fecha: datetime
    total_sin_descuento: float
    descuento: float
    total: float

class Config:
        from_attributes = True


class DevolucionDetalle(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0)

class DevolucionCreate(BaseModel):
    venta_id: Optional[int] = None
    detalles: List[DevolucionDetalle]

class Devolucion(BaseModel):
    id: int
    venta_id: Optional[int]
    fecha: datetime
    detalles: List[DevolucionDetalle]

    class Config:
        orm_mode = True