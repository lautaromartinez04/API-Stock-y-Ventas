from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from config.database import Session
from schemas.venta import Venta, VentaCreate
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
def get_ventas():
    db = Session()
    return VentaService(db).get_all()

@ventas_router.get(
    "/ventas/{id}",
    response_model=Venta,
    tags=["Ventas"],
    dependencies=[Depends(JWTBearer())]
)
def get_venta(id: int):
    db = Session()
    venta = VentaService(db).get(id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

@ventas_router.post(
    "/ventas",
    response_model=Venta,
    tags=["Ventas"],
    dependencies=[Depends(JWTBearer())]
)
def create_venta(
    venta: VentaCreate,
    background_tasks: BackgroundTasks
):
    db = Session()
    try:
        result = VentaService(db).create(venta)

        # notificar nueva venta
        background_tasks.add_task(
            manager.broadcast,
            {
                "event": "new_sale",
                "venta_id": result.id,
                "total": result.total,
                "cliente_id": result.cliente_id,
                "detalles": [d.dict() for d in venta.detalles]
            },
            "ventas"
        )

        # notificar stock actualizado
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
def update_venta(id: int, venta: VentaCreate):
    db = Session()
    updated = VentaService(db).update(id, venta)
    if not updated:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return updated

@ventas_router.delete(
    "/ventas/{id}",
    tags=["Ventas"],
    dependencies=[Depends(JWTBearer())]
)
def delete_venta(id: int):
    db = Session()
    VentaService(db).delete(id)
    return JSONResponse(status_code=200, content={"message": "Venta eliminada"})
