from pydantic import BaseModel, ConfigDict
from typing import Optional

class ClienteBase(BaseModel):
    nombre: str
    documento: Optional[str]
    direccion: Optional[str]
    telefono: Optional[str]

class ClienteCreate(ClienteBase):
    pass

class Cliente(ClienteBase):
    id: int

    # Permite aceptar instancias de SQLAlchemy al devolver datos
    model_config = ConfigDict(from_attributes=True)
