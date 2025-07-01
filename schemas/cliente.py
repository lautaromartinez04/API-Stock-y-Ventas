from pydantic import BaseModel
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

    class Config:
        from_attributes = True
