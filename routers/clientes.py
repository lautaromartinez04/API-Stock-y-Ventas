from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from config.database import Session
from models.clientes import Cliente as ClienteModel
from schemas.cliente import Cliente, ClienteCreate
from services.clientes import ClienteService

clientes_router = APIRouter()

@clientes_router.get("/clientes", response_model=list[Cliente], tags=["Clientes"])
def get_clientes():
    db = Session()
    result = ClienteService(db).get_all()
    return result

@clientes_router.get("/clientes/{id}", response_model=Cliente, tags=["Clientes"])
def get_cliente(id: int):
    db = Session()
    result = ClienteService(db).get(id)
    if not result:
        return JSONResponse(status_code=404, content={"message": "No encontrado"})
    return result

@clientes_router.post("/clientes", response_model=Cliente, tags=["Clientes"])
def create_cliente(cliente: ClienteCreate):
    db = Session()
    result = ClienteService(db).create(cliente)
    return result

@clientes_router.put("/clientes/{id}", response_model=Cliente, tags=["Clientes"])
def update_cliente(id: int, cliente: ClienteCreate):
    db = Session()
    result = ClienteService(db).update(id, cliente)
    if not result:
        return JSONResponse(status_code=404, content={"message": "No encontrado"})
    return result

@clientes_router.delete("/clientes/{id}", tags=["Clientes"])
def delete_cliente(id: int):
    db = Session()
    result = ClienteService(db).delete(id)
    return JSONResponse(status_code=200, content={"message": "Se ha eliminado el cliente"})
