from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Este lo vas a usar en la creación de la venta
class DetalleVentaCreate(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float

class VentaBase(BaseModel):
    total: float
    cliente_id: Optional[int]
    usuario_id: int

# Este schema ahora incluye los detalles
class VentaCreate(VentaBase):
    detalles: List[DetalleVentaCreate]

# Este se usa para devolver una venta con ID y fecha
class Venta(VentaBase):
    id: int
    fecha: datetime

    class Config:
        from_attributes = True
