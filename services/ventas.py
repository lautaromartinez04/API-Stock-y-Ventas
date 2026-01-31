# src/services/ventas.py

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from models.ventas import Venta as VentaModel
from models.detalle_venta import DetalleVenta as DetalleVentaModel
from models.productos import Producto as ProductoModel
from schemas.venta import VentaCreate, Venta

class VentaService:
    def __init__(self, db):
        self.db = db

    def get_all(self) -> list[Venta]:
        ventas = self.db.query(VentaModel).order_by(VentaModel.fecha.desc(), VentaModel.id.desc()).all()
        return [Venta.model_validate(v) for v in ventas]

    def get(self, id: int) -> Venta | None:
        v = (
            self.db.query(VentaModel)
            .filter(VentaModel.id == id)
            .first()
        )
        if not v:
            return None
        return Venta.model_validate(v)

    def create(self, payload: VentaCreate) -> Venta:
        try:
            # 1) Calcular bruto (sin descuentos)
            gross_total = sum(d.precio_unitario * d.cantidad for d in payload.detalles)

            # 2) Validar y calcular después de descuentos individuales
            net_after_individual = 0.0
            for d in payload.detalles:
                if not (0 <= d.descuento_individual <= 100):
                    raise HTTPException(
                        status_code=400,
                        detail="Descuento individual debe estar entre 0 y 100"
                    )
                net_after_individual += (
                    d.precio_unitario
                    * d.cantidad
                    * (1 - d.descuento_individual / 100)
                )

            # 3) Validar descuento global
            pct_global = payload.descuento or 0.0
            if not (0 <= pct_global <= 100):
                raise HTTPException(
                    status_code=400,
                    detail="Descuento global debe estar entre 0 y 100"
                )

            # 4) Calcular total neto final
            total_neto = net_after_individual * (1 - pct_global / 100)

            # 5) Crear cabecera de la venta con forma_pago y pagado
            venta = VentaModel(
                cliente_id          = payload.cliente_id,
                usuario_id          = payload.usuario_id,
                total_sin_descuento = gross_total,
                descuento           = pct_global,
                total               = total_neto,
                forma_pago          = payload.forma_pago,
                pagado              = payload.pagado
            )
            self.db.add(venta)
            self.db.flush()  # para obtener venta.id

            # 6) Procesar cada detalle: stock y registro
            for d in payload.detalles:
                prod = (
                    self.db.query(ProductoModel)
                    .filter(ProductoModel.id == d.producto_id)
                    .first()
                )
                if not prod:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Producto {d.producto_id} no existe"
                    )
                if prod.stock_actual < d.cantidad:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Stock insuficiente para '{prod.nombre}'; "
                            f"disponible {prod.stock_actual}"
                        )
                    )
                # descontar stock
                prod.stock_actual -= d.cantidad
                self.db.add(prod)

                # recalcular subtotal de la línea con descuento individual
                line_subtotal = (
                    d.precio_unitario
                    * d.cantidad
                    * (1 - d.descuento_individual / 100)
                )

                detalle = DetalleVentaModel(
                    venta_id             = venta.id,
                    producto_id          = d.producto_id,
                    cantidad             = d.cantidad,
                    precio_unitario      = d.precio_unitario,
                    descuento_individual = d.descuento_individual,
                    subtotal             = line_subtotal,
                    costo_unitario       = prod.precio_costo # Guardamos el costo histórico
                )
                self.db.add(detalle)

            # 7) Commit y refrescar
            self.db.commit()
            self.db.refresh(venta)
            return Venta.model_validate(venta)

        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error interno al crear la venta"
            )

    def update(self, id: int, payload: VentaCreate) -> Venta | None:
        venta = (
            self.db.query(VentaModel)
            .filter(VentaModel.id == id)
            .first()
        )
        if not venta:
            return None

        # Actualiza cabecera: totales, forma_pago y pagado
        total_bruto = sum(d.subtotal for d in payload.detalles)
        pct = payload.descuento or 0.0
        total_neto = total_bruto * (1 - pct / 100)

        venta.cliente_id          = payload.cliente_id
        venta.usuario_id          = payload.usuario_id
        venta.total_sin_descuento = total_bruto
        venta.descuento           = pct
        venta.total               = total_neto
        venta.forma_pago          = payload.forma_pago
        venta.pagado              = payload.pagado

        self.db.commit()
        self.db.refresh(venta)
        return Venta.model_validate(venta)

    def delete(self, id: int) -> None:
        self.db.query(VentaModel).filter(VentaModel.id == id).delete()
        self.db.commit()

    def mark_pagado(self, id: int, pagado: bool) -> Venta:
        venta = (
            self.db.query(VentaModel)
            .filter(VentaModel.id == id)
            .first()
        )
        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        venta.pagado = pagado
        self.db.commit()
        self.db.refresh(venta)
        return Venta.model_validate(venta)
