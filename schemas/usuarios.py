from pydantic import BaseModel, Field

# Para el login
class User(BaseModel):
    username: str
    password: str

# Datos comunes de usuario
class UsuarioBase(BaseModel):
    id: int
    username: str = Field(min_length=4, max_length=20)
    role: str = Field(min_length=4, max_length=20)

    class Config:
        from_attributes = True

# Insertar o devolver usuario completo (incluye password y role)
class Usuarios(UsuarioBase):
    password: str = Field(min_length=4)
