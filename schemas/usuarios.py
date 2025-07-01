from pydantic import BaseModel, Field

# Para el login
class User(BaseModel):
    username: str
    password: str

# Usuario básico solo con username y password
class UsuarioBase(BaseModel):
    id: int
    username: str = Field(min_length=4, max_length=20)  # Solo username

    class Config:
        from_attributes = True

# Usuario completo solo con username y password
class Usuarios(UsuarioBase):
    password: str = Field(min_length=4)  # Solo password
    
