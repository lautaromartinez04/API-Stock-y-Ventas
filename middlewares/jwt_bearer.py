from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException
from services.usuarios import UsuariosService
from utils.jwt_manager import validate_token
from models.usuarios import Usuarios as UsuarioModel
from config.database import Session

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)

        db = Session()
        usuariosDb: list[UsuarioModel] = UsuariosService(db).get_usuarios()

        for item in usuariosDb:
            if item.username == data['username']:  # ahora se valida contra el campo real
                return

        raise HTTPException(status_code=403, detail="Credenciales inválidas")