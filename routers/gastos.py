# routers/gastos.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from config.database import get_db
from middlewares.jwt_bearer import JWTBearer
from schemas.gasto import Gasto, GastoCreate
from services.gastos import GastoService

gastos_router = APIRouter(tags=["Gastos"], dependencies=[Depends(JWTBearer())])

@gastos_router.get(
    "/gastos",
    response_model=list[Gasto]
)
def list_gastos(db: Session = Depends(get_db)):
    return GastoService(db).get_all()

@gastos_router.get(
    "/gastos/{id}",
    response_model=Gasto
)
def get_gasto(id: int, db: Session = Depends(get_db)):
    gasto = GastoService(db).get(id)
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return gasto

@gastos_router.post(
    "/gastos",
    response_model=Gasto,
    status_code=status.HTTP_201_CREATED
)
def create_gasto(gasto: GastoCreate, db: Session = Depends(get_db)):
    return GastoService(db).create(gasto)

@gastos_router.put(
    "/gastos/{id}",
    response_model=Gasto
)
def update_gasto(id: int, gasto: GastoCreate, db: Session = Depends(get_db)):
    updated = GastoService(db).update(id, gasto)
    if not updated:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return updated

@gastos_router.delete(
    "/gastos/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_gasto(id: int, db: Session = Depends(get_db)):
    GastoService(db).delete(id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
