from fastapi import APIRouter, Depends, Path, HTTPException, status
from fastapi.responses import JSONResponse
from config.database import Session
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
    return Usuarios.from_orm(user)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(users: list, username: str) -> Optional[UsuarioModel]:
    for item in users:
        if item.username == username:
            return item
    return None

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@usuarios_router.post('/login', tags=['auth'])
def login(user: User):
    db = Session()
    usuarios_db: list = UsuariosService(db).get_usuarios()

    usuario = authenticate_user(usuarios_db, user.username, user.password)
    if not usuario:
        return JSONResponse(status_code=401, content={'accesoOk': False, 'token': ''})
    
    token: str = create_token(usuario.model_dump())
    return JSONResponse(status_code=200, content={'accesoOk': True, 'token': token, 'usuario': jsonable_encoder(usuario)})

@usuarios_router.get('/usuarios', response_model=list[Usuarios], tags=['Usuarios'])
def get_usuarios():
    db = Session()
    result = UsuariosService(db).get_usuarios()
    return result

@usuarios_router.post('/usuarios', tags=['Usuarios'], response_model=dict, status_code=201)
def create_usuarios(usuario: Usuarios) -> dict:
    usuario.password = get_password_hash(usuario.password)
    db = Session()
    UsuariosService(db).create_usuarios(usuario)
    return JSONResponse(status_code=201, content={"message": "Se ha registrado el usuario"})

@usuarios_router.put('/usuarios/{id}', tags=['Usuarios'], response_model=dict, status_code=200)
def update_usuarios(id: int, usuario: Usuarios) -> dict:
    db = Session()
    result = UsuariosService(db).get_usuario(id)
    if not result:
        return JSONResponse(status_code=404, content={'message': "No encontrado"})
    
    usuario.password = get_password_hash(usuario.password)
    UsuariosService(db).update_usuarios(id, usuario)
    return JSONResponse(status_code=200, content={"message": "Se ha modificado el usuario"})

@usuarios_router.delete('/usuarios/{id}', tags=['Usuarios'], response_model=dict, status_code=200)
def delete_usuarios(id: int) -> dict:
    db = Session()
    result: UsuarioModel = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
    if not result:
        return JSONResponse(status_code=404, content={"message": "No se encontró"})
    UsuariosService(db).delete_usuarios(id)
    return JSONResponse(status_code=200, content={"message": "Se ha eliminado el usuario"})

