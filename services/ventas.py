from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from config.database import Session
from models.ventas import Venta as VentaModel
from models.detalle_venta import DetalleVenta as DetalleVentaModel
from models.productos import Producto as ProductoModel
from schemas.venta import VentaCreate, Venta

class VentaService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Venta]:
        ventas = self.db.query(VentaModel).all()
        return [Venta.model_validate(v) for v in ventas]

    def get(self, id: int) -> Venta | None:
        v = self.db.query(VentaModel).filter(VentaModel.id == id).first()
        if not v:
            return None
        return Venta.model_validate(v)

    def create(self, payload: VentaCreate) -> Venta:
        try:
            # 1) Total bruto
            total_bruto = sum(d.subtotal for d in payload.detalles)
            # 2) Validar porcentaje de descuento
            pct = payload.descuento or 0.0
            if pct < 0 or pct > 100:
                raise HTTPException(status_code=400, detail="Descuento debe estar entre 0 y 100")
            # 3) Calcular total neto
            total_neto = total_bruto * (1 - pct / 100)

            # 4) Crear cabecera de la venta
            venta = VentaModel(
                cliente_id          = payload.cliente_id,
                usuario_id          = payload.usuario_id,
                total_sin_descuento = total_bruto,
                descuento           = pct,
                total               = total_neto
            )
            self.db.add(venta)
            self.db.flush()  # obtiene venta.id

            # 5) Procesar detalles (validar stock y descontar)
            for d in payload.detalles:
                producto = (
                    self.db.query(ProductoModel)
                    .filter(ProductoModel.id == d.producto_id)
                    .first()
                )
                if not producto:
                    raise HTTPException(status_code=404, detail=f"Producto {d.producto_id} no existe")
                if producto.stock_actual < d.cantidad:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuficiente para '{producto.nombre}', disponible {producto.stock_actual}"
                    )
                producto.stock_actual -= d.cantidad

                detalle = DetalleVentaModel(
                    venta_id       = venta.id,
                    producto_id    = d.producto_id,
                    cantidad       = d.cantidad,
                    precio_unitario= d.precio_unitario,
                    subtotal       = d.subtotal
                )
                self.db.add(detalle)

            # 6) Commit y refresh
            self.db.commit()
            self.db.refresh(venta)
            return Venta.model_validate(venta)

        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Error interno al crear la venta")

    def update(self, id: int, payload: VentaCreate) -> Venta | None:
        venta = self.db.query(VentaModel).filter(VentaModel.id == id).first()
        if not venta:
            return None

        # Actualiza sólo cabecera; no tocamos detalles aquí
        total_bruto = sum(d.subtotal for d in payload.detalles)
        pct = payload.descuento or 0.0
        total_neto = total_bruto * (1 - pct / 100)

        for field, value in {
            "cliente_id": payload.cliente_id,
            "usuario_id": payload.usuario_id,
            "total_sin_descuento": total_bruto,
            "descuento": pct,
            "total": total_neto
        }.items():
            setattr(venta, field, value)

        self.db.commit()
        self.db.refresh(venta)
        return Venta.model_validate(venta)

    def delete(self, id: int) -> None:
        self.db.query(VentaModel).filter(VentaModel.id == id).delete()
        self.db.commit()
