from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class DetalleVentaCreate(BaseModel):
    producto_id: int
    cantidad: float
    precio_unitario: float
    subtotal: float
    descuento_individual: float

class VentaBase(BaseModel):
    cliente_id: Optional[int]
    usuario_id: int

class VentaCreate(VentaBase):
    detalles: List[DetalleVentaCreate]
    descuento: Optional[float] = Field(
        0.0, ge=0, le=100, description="Porcentaje de descuento (0–100)"
    )
    forma_pago: str = Field(
        "efectivo",
        description="Forma de pago (ej. 'efectivo', 'tarjeta', 'transferencia')"
    )
    pagado: bool = Field(
        False,
        description="Indica si la venta ya fue pagada"
    )

class Venta(VentaBase):
    id: int
    fecha: datetime
    total_sin_descuento: float
    descuento: float
    total: float
    forma_pago: str
    pagado: bool

    # Aquí va la config para aceptar instancias de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

class VentaPatch(BaseModel):
    pagado: bool = Field(..., description="Marcar la venta como pagada o no")
