from models.usuarios import Usuarios as UsuariosModel
from schemas.usuarios import Usuarios


class UsuariosService():
    
    def __init__(self, db) -> None:
        self.db = db

    def get_usuarios(self):
        result = self.db.query(UsuariosModel).all()
        return [Usuarios.model_validate(u) for u in result]

    def get_usuario(self, id):
        # Devuelve un usuario por su ID
        result = self.db.query(UsuariosModel).filter(UsuariosModel.id == id).first()
        return result

    def create_usuarios(self, usuario: Usuarios):
        # Crea un nuevo usuario con username y password
        new_usuario = UsuariosModel(username=usuario.username, password=usuario.password)
        self.db.add(new_usuario)
        self.db.commit()
        return new_usuario

    def update_usuarios(self, id: int, data: Usuarios):
        # Actualiza el usuario con el id proporcionado (solo username y password)
        usuario = self.db.query(UsuariosModel).filter(UsuariosModel.id == id).first()
        if not usuario:
            return None  # Si no se encuentra el usuario, devolvemos None
        
        usuario.username = data.username  # Solo actualizamos username y password
        usuario.password = data.password
        
        self.db.commit()
        return usuario

    def delete_usuarios(self, id: int):
        # Elimina un usuario por su ID
        self.db.query(UsuariosModel).filter(UsuariosModel.id == id).delete()
        self.db.commit()
        return
