from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VentaBase(BaseModel):
    total: float
    cliente_id: Optional[int]
    usuario_id: int

class VentaCreate(VentaBase):
    pass

class Venta(VentaBase):
    id: int
    fecha: datetime

    class Config:
        from_attributes = True
