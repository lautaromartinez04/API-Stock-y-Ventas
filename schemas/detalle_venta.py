from pydantic import BaseModel

class DetalleVentaBase(BaseModel):
    venta_id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float

class DetalleVentaCreate(DetalleVentaBase):
    pass

class DetalleVenta(DetalleVentaBase):
    id: int

    class Config:
        from_attributes = True
