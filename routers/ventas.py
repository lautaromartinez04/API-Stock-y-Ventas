from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from config.database import Session
from schemas.venta import Venta, VentaCreate
from services.ventas import VentaService
from middlewares.jwt_bearer import JWTBearer

ventas_router = APIRouter()

@ventas_router.get("/ventas",response_model=list[Venta],tags=["Ventas"], dependencies=[Depends(JWTBearer())])
def get_ventas():
    db = Session()
    result = VentaService(db).get_all()
    return result

@ventas_router.get( "/ventas/{id}", response_model=Venta, tags=["Ventas"], dependencies=[Depends(JWTBearer())])
def get_venta(id: int):
    db = Session()
    result = VentaService(db).get(id)
    if not result:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return result

@ventas_router.post( "/ventas", response_model=Venta, tags=["Ventas"], dependencies=[Depends(JWTBearer())])
def create_venta(venta: VentaCreate):
    db = Session()
    try:
        result = VentaService(db).create(venta)
        return result
    except HTTPException:
        # HTTPException ya viene con su status_code y detail
        raise
    except Exception as e:
        # Cualquier otro error
        raise HTTPException(status_code=500, detail="Error al crear la venta")

@ventas_router.put( "/ventas/{id}", response_model=Venta, tags=["Ventas"], dependencies=[Depends(JWTBearer())])
def update_venta(id: int, venta: VentaCreate):
    db = Session()
    result = VentaService(db).update(id, venta)
    if not result:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return result

@ventas_router.delete("/ventas/{id}", tags=["Ventas"], dependencies=[Depends(JWTBearer())])
def delete_venta(id: int):
    db = Session()
    VentaService(db).delete(id)
    return JSONResponse(status_code=200, content={"message": "Venta eliminada"})
