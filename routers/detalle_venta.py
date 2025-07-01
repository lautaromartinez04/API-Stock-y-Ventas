from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from config.database import Session
from models.detalle_venta import DetalleVenta as DetalleVentaModel
from schemas.detalle_venta import DetalleVenta, DetalleVentaCreate
from services.detalle_venta import DetalleVentaService

detalle_ventas_router = APIRouter()

@detalle_ventas_router.get("/detalle_ventas", response_model=list[DetalleVenta], tags=["Detalle de ventas"])
def get_detalle_ventas():
    db = Session()
    result = DetalleVentaService(db).get_all()
    return result

@detalle_ventas_router.get("/detalle_ventas/{id}", response_model=DetalleVenta, tags=["Detalle de ventas"])
def get_detalle_venta(id: int):
    db = Session()
    result = DetalleVentaService(db).get(id)
    if not result:
        return JSONResponse(status_code=404, content={"message": "No encontrado"})
    return result

@detalle_ventas_router.post("/detalle_ventas", response_model=DetalleVenta, tags=["Detalle de ventas"])
def create_detalle_venta(detalle: DetalleVentaCreate):
    db = Session()
    result = DetalleVentaService(db).create(detalle)
    return result

@detalle_ventas_router.put("/detalle_ventas/{id}", response_model=DetalleVenta, tags=["Detalle de ventas"])
def update_detalle_venta(id: int, detalle: DetalleVentaCreate):
    db = Session()
    result = DetalleVentaService(db).update(id, detalle)
    if not result:
        return JSONResponse(status_code=404, content={"message": "No encontrado"})
    return result

@detalle_ventas_router.delete("/detalle_ventas/{id}", tags=["Detalle de ventas"])
def delete_detalle_venta(id: int):
    db = Session()
    result = DetalleVentaService(db).delete(id)
    return JSONResponse(status_code=200, content={"message": "Se ha eliminado el detalle de venta"})
