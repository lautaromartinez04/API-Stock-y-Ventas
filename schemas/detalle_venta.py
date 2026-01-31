from pydantic import BaseModel, ConfigDict

class DetalleVentaBase(BaseModel):
    venta_id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float
    descuento_individual: float
    costo_unitario: float | None = 0

class DetalleVentaCreate(DetalleVentaBase):
    pass

class DetalleVenta(DetalleVentaBase):
    id: int

    # Permite aceptar instancias del ORM (SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)
