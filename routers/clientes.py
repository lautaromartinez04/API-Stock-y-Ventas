from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.database import get_db
from models.clientes import Cliente as ClienteModel
from schemas.cliente import Cliente, ClienteCreate
from services.clientes import ClienteService
from middlewares.jwt_bearer import JWTBearer

clientes_router = APIRouter()

@clientes_router.get(
    "/clientes",
    response_model=list[Cliente],
    tags=["Clientes"],
    dependencies=[Depends(JWTBearer())]
)
def get_clientes(db: Session = Depends(get_db)):
    result = ClienteService(db).get_all()
    return result

@clientes_router.get(
    "/clientes/{id}",
    response_model=Cliente,
    tags=["Clientes"],
    dependencies=[Depends(JWTBearer())]
)
def get_cliente(id: int, db: Session = Depends(get_db)):
    result = ClienteService(db).get(id)
    if not result:
        return JSONResponse(status_code=404, content={"message": "No encontrado"})
    return result

@clientes_router.post(
    "/clientes",
    response_model=Cliente,
    tags=["Clientes"],
    dependencies=[Depends(JWTBearer())]
)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    result = ClienteService(db).create(cliente)
    return result

@clientes_router.put(
    "/clientes/{id}",
    response_model=Cliente,
    tags=["Clientes"],
    dependencies=[Depends(JWTBearer())]
)
def update_cliente(id: int, cliente: ClienteCreate, db: Session = Depends(get_db)):
    result = ClienteService(db).update(id, cliente)
    if not result:
        return JSONResponse(status_code=404, content={"message": "No encontrado"})
    return result

@clientes_router.delete(
    "/clientes/{id}",
    tags=["Clientes"],
    dependencies=[Depends(JWTBearer())]
)
def delete_cliente(id: int, db: Session = Depends(get_db)):
    ClienteService(db).delete(id)
    return JSONResponse(status_code=200, content={"message": "Se ha eliminado el cliente"})