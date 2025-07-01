from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from config.database import Session
from models.ventas import Venta as VentaModel
from schemas.venta import Venta, VentaCreate
from services.ventas import VentaService

ventas_router = APIRouter()

@ventas_router.get("/ventas", response_model=list[Venta], tags=["Ventas"])
def get_ventas():
    db = Session()
    result = VentaService(db).get_all()
    return result

@ventas_router.get("/ventas/{id}", response_model=Venta, tags=["Ventas"])
def get_venta(id: int):
    db = Session()
    result = VentaService(db).get(id)
    if not result:
        return JSONResponse(status_code=404, content={"message": "No encontrado"})
    return result

@ventas_router.post("/ventas", response_model=Venta, tags=["Ventas"])
def create_venta(venta: VentaCreate):
    db = Session()
    result = VentaService(db).create(venta)
    return result

@ventas_router.put("/ventas/{id}", response_model=Venta, tags=["Ventas"])
def update_venta(id: int, venta: VentaCreate):
    db = Session()
    result = VentaService(db).update(id, venta)
    if not result:
        return JSONResponse(status_code=404, content={"message": "No encontrado"})
    return result

@ventas_router.delete("/ventas/{id}", tags=["Ventas"])
def delete_venta(id: int):
    db = Session()
    result = VentaService(db).delete(id)
    return JSONResponse(status_code=200, content={"message": "Se ha eliminado la venta"})
