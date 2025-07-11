from pydantic import BaseModel, Field
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    codigo: str
    descripcion: Optional[str] = None

    stock_actual: int = Field(
        0, ge=0, description="Stock disponible"
    )
    stock_bajo: int = Field(
        5, ge=0, description="Umbral mínimo para alerta de stock"
    )

    precio_costo: float = Field(
        0.0, ge=0, description="Precio de costo del producto"
    )
    margen: float = Field(
        25.0, ge=0, le=100, description="Margen de ganancia (%)"
    )
    precio_unitario: float = Field(
        ..., ge=0, description="Precio de venta"
    )

    categoria_id: Optional[int] = None
    activo: bool = True
    image_url: Optional[str] = None  # ruta o URL de la imagen

class ProductoCreate(ProductoBase):
    pass

class Producto(ProductoBase):
    id: int

    class Config:
        from_attributes = True
