from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.usuarios import UsuariosService
from utils.jwt_manager import validate_token
from models.usuarios import Usuarios as UsuarioModel
from config.database import SessionLocal

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        # Esto extrae el header y valida que tenga Bearer token
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        token = credentials.credentials

        # 1) Validar y decodificar JWT
        try:
            payload = validate_token(token)
        except Exception:
            raise HTTPException(status_code=403, detail="Token inválido o expirado")

        # 2) Abrir sesión y chequear que el usuario exista
        db = SessionLocal()
        try:
            usuarios_db: list[UsuarioModel] = UsuariosService(db).get_usuarios()
            if not any(u.username == payload["username"] for u in usuarios_db):
                raise HTTPException(status_code=403, detail="Usuario no encontrado")
        finally:
            db.close()

        # 3) Si todo está ok, devolvemos las credenciales para que FastAPI continúe
        return credentials