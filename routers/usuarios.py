# routers/usuarios.py

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
    def get_user(users, username):
        for u in users:
            if u.username == username:
                return u
        return None

    user = get_user(users, username)
    if not user or not pwd_context.verify(password, user.password):
        return None
    return Usuarios.model_validate(user)


@usuarios_router.post(
    "/login",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
    response_model=None,
)
def login(
    user: User,
    db: Session = Depends(get_db)
):
    usuarios_db = UsuariosService(db).get_usuarios()
    usuario = authenticate_user(usuarios_db, user.username, user.password)
    if not usuario:
        return JSONResponse(status_code=401, content={"accesoOk": False, "token": ""})

    token = create_token(usuario.model_dump())
    return JSONResponse(
        status_code=200,
        content={
            "accesoOk": True,
            "token": token,
            "usuario": jsonable_encoder(usuario),
        },
    )


@usuarios_router.get(
    "/usuarios",
    response_model=list[Usuarios],
    tags=["Usuarios"],
    dependencies=[Depends(JWTBearer())]
)
def get_usuarios(db: Session = Depends(get_db)):
    return UsuariosService(db).get_usuarios()


@usuarios_router.get(
    "/usuarios/{id}",
    response_model=Usuarios,
    tags=["Usuarios"],
    dependencies=[Depends(JWTBearer())]
)
def get_usuario(
    id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    usuario = UsuariosService(db).get_usuario(id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@usuarios_router.post(
    "/usuarios",
    response_model=Usuarios,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuarios"]
)
def create_usuarios(
    usuario: Usuarios,
    db: Session = Depends(get_db)
):
    usuario.password = pwd_context.hash(usuario.password)
    return UsuariosService(db).create_usuarios(usuario)


@usuarios_router.put(
    "/usuarios/{id}",
    response_model=Usuarios,
    status_code=status.HTTP_200_OK,
    tags=["Usuarios"],
    dependencies=[Depends(JWTBearer())]
)
def update_usuarios(
    id: int = Path(..., gt=0),
    usuario_in: Usuarios = Depends(),
    db: Session = Depends(get_db)
):
    existing = UsuariosService(db).get_usuario(id)
    if not existing:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario_in.password = pwd_context.hash(usuario_in.password)
    return UsuariosService(db).update_usuarios(id, usuario_in)


@usuarios_router.delete(
    "/usuarios/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Usuarios"],
    dependencies=[Depends(JWTBearer())]
)
def delete_usuarios(
    id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    if not db.query(UsuarioModel).filter(UsuarioModel.id == id).first():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    UsuariosService(db).delete_usuarios(id)
    return JSONResponse(status_code=204, content=None)
