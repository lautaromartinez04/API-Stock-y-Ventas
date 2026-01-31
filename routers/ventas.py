# src/routers/ventas.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import Body
from config.database import get_db
from schemas.venta import Venta, VentaCreate, VentaPatch
from services.ventas import VentaService
from middlewares.jwt_bearer import JWTBearer
from utils.connection_manager import manager
from models.productos import Producto as ProductoModel

ventas_router = APIRouter()

@ventas_router.get(
    "/ventas",
    response_model=list[Venta],
    tags=["Ventas"],
    dependencies=[Depends(JWTBearer())]
)
def get_ventas(db: Session = Depends(get_db)):
    return VentaService(db).get_all()

@ventas_router.get(
    "/ventas/{id}",
    response_model=Venta,
    tags=["Ventas"],
    dependencies=[Depends(JWTBearer())]
)
def get_venta(id: int, db: Session = Depends(get_db)):
    venta = VentaService(db).get(id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

@ventas_router.post(
    "/ventas",
    response_model=Venta,
    status_code=status.HTTP_201_CREATED,
    tags=["Ventas"],
    dependencies=[Depends(JWTBearer())]
)
def create_venta(
    venta: VentaCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        result = VentaService(db).create(venta)

        # Notificar nueva venta
        background_tasks.add_task(
            manager.broadcast,
            {
                "event": "new_sale",
                "venta_id": result.id,
                "total_sin_descuento": result.total_sin_descuento,
                "descuento": result.descuento,
                "total": result.total,
                "cliente_id": result.cliente_id,
                "forma_pago": result.forma_pago,
                "pagado": result.pagado,
                "detalles": [d.dict() for d in venta.detalles]
            },
            "ventas"
        )

        # Notificar stock actualizado
        for d in venta.detalles:
            prod = db.query(ProductoModel).filter(ProductoModel.id == d.producto_id).first()
            background_tasks.add_task(
                manager.broadcast,
                {
                    "event": "stock_update",
                    "producto_id": prod.id,
                    "new_stock": prod.stock_actual
                },
                "stock"
            )

        return result

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la venta"
        )

@ventas_router.put(
    "/ventas/{id}",
    response_model=Venta,
    tags=["Ventas"],
    dependencies=[Depends(JWTBearer())]
)
def update_venta(
    id: int,
    venta: VentaCreate,
    db: Session = Depends(get_db)
):
    updated = VentaService(db).update(id, venta)
    if not updated:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return updated

@ventas_router.delete(
    "/ventas/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Ventas"],
    dependencies=[Depends(JWTBearer())]
)
def delete_venta(id: int, db: Session = Depends(get_db)):
    VentaService(db).delete(id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)

@ventas_router.post(
    "/ventas/{id}/confirmar",
    response_model=Venta,
    tags=["Ventas"],
    dependencies=[Depends(JWTBearer())]
)
def confirmar_venta(id: int, db: Session = Depends(get_db)):
    return VentaService(db).confirmar_venta(id)

@ventas_router.post(
    "/ventas/{id}/cancelar",
    response_model=Venta,
    tags=["Ventas"],
    dependencies=[Depends(JWTBearer())]
)
def cancelar_venta(id: int, db: Session = Depends(get_db)):
    return VentaService(db).cancelar_venta(id)

@ventas_router.patch(
    "/ventas/{id}/pagado",
    response_model=Venta,
    status_code=status.HTTP_200_OK,
    tags=["Ventas"],
    dependencies=[Depends(JWTBearer())]
)
def patch_venta_pagado(
    id: int,
    payload: VentaPatch,
    db: Session = Depends(get_db)
):
    try:
        return VentaService(db).mark_pagado(id, payload.pagado)
    except HTTPException:
        raise
