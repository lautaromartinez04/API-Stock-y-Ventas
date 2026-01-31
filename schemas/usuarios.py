from pydantic import BaseModel, Field, ConfigDict

# Para el login (solo entrada, no ORM)
class User(BaseModel):
    username: str
    password: str

# Datos comunes de usuario
class UsuarioBase(BaseModel):
    id: int
    username: str = Field(min_length=4, max_length=20)
    role: str = Field(min_length=4, max_length=20)

# Modelo que devuelve usuario completo (puede usarse también para creación)
class Usuarios(UsuarioBase):
    password: str = Field(min_length=4)

    # Este sí acepta instancias del ORM (SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)
