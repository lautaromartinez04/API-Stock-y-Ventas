from fastapi import APIRouter, Depends, Path, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.database import get_db
from models.usuarios import Usuarios as UsuarioModel
from fastapi.encoders import jsonable_encoder
from middlewares.jwt_bearer import JWTBearer
from services.usuarios import UsuariosService
from schemas.usuarios import Usuarios, User
from passlib.context import CryptContext
from utils.jwt_manager import create_token
from typing import Optional

usuarios_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate_user(users: list, username: str, password: str) -> Optional[Usuarios]:
    user = get_user(users, username)
    if not user or not verify_password(password, user.password):
        return False
    return Usuarios.model_validate(user)


def get_user(users: list, username: str) -> Optional[UsuarioModel]:
    for item in users:
        if item.username == username:
            return item
    return None


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

@usuarios_router.post('/login', tags=['auth'], status_code=status.HTTP_200_OK)
def login(user: User, db: Session = Depends(get_db)):
    usuarios_db: list = UsuariosService(db).get_usuarios()
    usuario = authenticate_user(usuarios_db, user.username, user.password)
    if not usuario:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={'accesoOk': False, 'token': ''})

    token: str = create_token(usuario.model_dump())
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'accesoOk': True,
            'token': token,
            'usuario': jsonable_encoder(usuario)
        }
    )

@usuarios_router.get(
    '/usuarios',
    response_model=list[Usuarios],
    tags=['Usuarios'],
    dependencies=[Depends(JWTBearer())]
)
def get_usuarios(db: Session = Depends(get_db)):
    return UsuariosService(db).get_usuarios()

@usuarios_router.post(
    '/usuarios',
    tags=['Usuarios'],
    response_model=Usuarios,
    status_code=status.HTTP_201_CREATED
)
def create_usuarios(usuario: Usuarios, db: Session = Depends(get_db)) -> Usuarios:
    usuario.password = get_password_hash(usuario.password)
    return UsuariosService(db).create_usuarios(usuario)

@usuarios_router.put(
    '/usuarios/{id}',
    tags=['Usuarios'],
    response_model=Usuarios,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(JWTBearer())]
)
def update_usuarios(
    id: int = Path(..., gt=0),
    usuario: Usuarios = Depends(),
    db: Session = Depends(get_db)
) -> Usuarios:
    existing = UsuariosService(db).get_usuario(id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    usuario.password = get_password_hash(usuario.password)
    return UsuariosService(db).update_usuarios(id, usuario)

@usuarios_router.delete(
    '/usuarios/{id}',
    tags=['Usuarios'],
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(JWTBearer())]
)
def delete_usuarios(
    id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    existing: UsuarioModel = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    UsuariosService(db).delete_usuarios(id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)