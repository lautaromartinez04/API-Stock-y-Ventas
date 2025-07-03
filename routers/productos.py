from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from config.database import Session
from models.productos import Producto as ProductoModel
from schemas.producto import Producto, ProductoCreate
from services.productos import ProductoService
from middlewares.jwt_bearer import JWTBearer

productos_router = APIRouter()

@productos_router.get("/productos", response_model=list[Producto], tags=["Productos"], dependencies=[Depends(JWTBearer())])
def get_productos():
    db = Session()
    result = ProductoService(db).get_all()
    return result

@productos_router.get("/productos/{id}", response_model=Producto, tags=["Productos"], dependencies=[Depends(JWTBearer())])
def get_producto(id: int):
    db = Session()
    result = ProductoService(db).get(id)
    if not result:
        return JSONResponse(status_code=404, content={"message": "No encontrado"})
    return result

@productos_router.post("/productos", response_model=Producto, tags=["Productos"], dependencies=[Depends(JWTBearer())])
def create_producto(producto: ProductoCreate):
    db = Session()
    result = ProductoService(db).create(producto)
    return result

@productos_router.put("/productos/{id}", response_model=Producto, tags=["Productos"], dependencies=[Depends(JWTBearer())])
def update_producto(id: int, producto: ProductoCreate):
    db = Session()
    result = ProductoService(db).update(id, producto)
    if not result:
        return JSONResponse(status_code=404, content={"message": "No encontrado"})
    return result

@productos_router.delete("/productos/{id}", tags=["Productos"], dependencies=[Depends(JWTBearer())])
def delete_producto(id: int):
    db = Session()
    result = ProductoService(db).delete(id)
    return JSONResponse(status_code=200, content={"message": "Se ha eliminado el producto"})
