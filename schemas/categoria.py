from pydantic import BaseModel, ConfigDict

class CategoriaBase(BaseModel):
    nombre: str

    model_config = ConfigDict(from_attributes=True)

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
