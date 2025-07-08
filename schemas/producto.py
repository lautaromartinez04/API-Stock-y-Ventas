from pydantic import BaseModel
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    codigo: str
    descripcion: Optional[str] = None
    stock_actual: Optional[int] = 0
    precio_unitario: float
    categoria_id: Optional[int]
    activo: Optional[bool] = True

class ProductoCreate(ProductoBase):
    image_url: Optional[str] = None  # Ahora acepta imagen opcional

class Producto(ProductoBase):
    id: int
    image_url: Optional[str] = None  # ruta o URL de la imagen

    class Config:
        from_attributes = True
