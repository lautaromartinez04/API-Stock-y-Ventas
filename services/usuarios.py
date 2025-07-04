from models.usuarios import Usuarios as UsuariosModel
from schemas.usuarios import Usuarios

class UsuariosService:
    
    def __init__(self, db) -> None:
        self.db = db

    def get_usuarios(self) -> list[Usuarios]:
        result = self.db.query(UsuariosModel).all()
        # Devuelve instancias Pydantic incluyendo el role
        return [Usuarios.model_validate(u) for u in result]

    def get_usuario(self, id: int) -> UsuariosModel | None:
        return self.db.query(UsuariosModel).filter(UsuariosModel.id == id).first()

    def create_usuarios(self, usuario: Usuarios) -> UsuariosModel:
        # Ahora incluimos el campo role al crear
        new_usuario = UsuariosModel(
            username=usuario.username,
            password=usuario.password,
            role=usuario.role
        )
        self.db.add(new_usuario)
        self.db.commit()
        self.db.refresh(new_usuario)
        return new_usuario

    def update_usuarios(self, id: int, data: Usuarios) -> UsuariosModel | None:
        usuario = self.db.query(UsuariosModel).filter(UsuariosModel.id == id).first()
        if not usuario:
            return None
        
        # Actualizamos username, password y role
        usuario.username = data.username
        usuario.password = data.password
        usuario.role = data.role
        
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def delete_usuarios(self, id: int) -> None:
        self.db.query(UsuariosModel).filter(UsuariosModel.id == id).delete()
        self.db.commit()
