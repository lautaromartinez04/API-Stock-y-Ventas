from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class GastoBase(BaseModel):
    fecha: datetime | None = None
    monto: float = Field(..., gt=0, description="Importe del gasto, debe ser > 0")
    descripcion: str | None = None
    usuario_id: int

class GastoCreate(BaseModel):
    monto: float = Field(..., gt=0, description="Importe del gasto, debe ser > 0")
    descripcion: str | None = None
    usuario_id: int

class Gasto(GastoBase):
    id: int
    fecha: datetime

    # Permite validar instancias de SQLAlchemy directamente
    model_config = ConfigDict(from_attributes=True)
