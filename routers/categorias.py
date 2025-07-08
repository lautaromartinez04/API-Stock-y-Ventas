from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.database import get_db
from models.categorias import Categoria as CategoriaModel
from schemas.categoria import Categoria, CategoriaCreate
from services.categorias import CategoriaService
from middlewares.jwt_bearer import JWTBearer

categorias_router = APIRouter()

@categorias_router.get(
    "/categorias",
    response_model=list[Categoria],
    tags=["Categorías"],
    dependencies=[Depends(JWTBearer())]
)
def get_categorias(db: Session = Depends(get_db)):
    result = CategoriaService(db).get_all()
    return result

@categorias_router.get(
    "/categorias/{id}",
    response_model=Categoria,
    tags=["Categorías"],
    dependencies=[Depends(JWTBearer())]
)
def get_categoria(id: int, db: Session = Depends(get_db)):
    result = CategoriaService(db).get(id)
    if not result:
        return JSONResponse(status_code=404, content={"message": "No encontrado"})
    return result

@categorias_router.post(
    "/categorias",
    response_model=Categoria,
    tags=["Categorías"],
    dependencies=[Depends(JWTBearer())]
)
def create_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    result = CategoriaService(db).create(categoria)
    return result

@categorias_router.put(
    "/categorias/{id}",
    response_model=Categoria,
    tags=["Categorías"],
    dependencies=[Depends(JWTBearer())]
)
def update_categoria(id: int, categoria: CategoriaCreate, db: Session = Depends(get_db)):
    result = CategoriaService(db).update(id, categoria)
    if not result:
        return JSONResponse(status_code=404, content={"message": "No encontrado"})
    return result

@categorias_router.delete(
    "/categorias/{id}",
    tags=["Categorías"],
    dependencies=[Depends(JWTBearer())]
)
def delete_categoria(id: int, db: Session = Depends(get_db)):
    CategoriaService(db).delete(id)
    return JSONResponse(status_code=200, content={"message": "Se ha eliminado la categoría"})