# services/devoluciones.py

from sqlalchemy.orm import Session
from sqlalchemy import func
import models.devoluciones as devol_models
import models.ventas as ventas_models
import models.productos as productos_models
import models.detalle_venta as dv_models
from schemas.devoluciones import DevolucionCreate


def create_devolucion(db: Session, data: DevolucionCreate) -> devol_models.Devolucion:
    """
    Crea una devolución y sus detalles asociados, y actualiza el stock_actual
    de los productos. Respeta precio_unitario y descuento_individual de la venta.
    """
    # 1) Verificar venta
    venta = db.query(ventas_models.Venta).filter(
        ventas_models.Venta.id == data.venta_id
    ).first()
    if not venta:
        raise ValueError("Venta no encontrada")

    # 2) Validar límite de devolución
    for item in data.items:
        sold_qty = db.query(func.coalesce(func.sum(dv_models.DetalleVenta.cantidad), 0)).filter(
            dv_models.DetalleVenta.venta_id == data.venta_id,
            dv_models.DetalleVenta.producto_id == item.producto_id
        ).scalar() or 0
        returned_qty = db.query(func.coalesce(func.sum(devol_models.DetalleDevolucion.cantidad), 0)).join(
            devol_models.Devolucion
        ).filter(
            devol_models.Devolucion.venta_id == data.venta_id,
            devol_models.DetalleDevolucion.producto_id == item.producto_id
        ).scalar() or 0
        if returned_qty + item.cantidad > sold_qty:
            disponible = sold_qty - returned_qty
            raise ValueError(
                f"No puedes devolver {item.cantidad} unidades del producto {item.producto_id}; "
                f"solo quedan {disponible} disponibles"
            )

    # 3) Crear cabecera
    nueva_dev = devol_models.Devolucion(
        venta_id=data.venta_id,
        reponer_stock=data.reponer_stock,
        detalle=data.detalle
    )
    db.add(nueva_dev)
    db.flush()

    # 4) Crear detalles usando datos de la venta original
    for item in data.items:
        # 4.1) Obtener detalle de venta original
        orig = (
            db.query(dv_models.DetalleVenta)
            .filter(
                dv_models.DetalleVenta.venta_id == data.venta_id,
                dv_models.DetalleVenta.producto_id == item.producto_id
            )
            .first()
        )
        if not orig:
            raise ValueError(f"Detalle de venta no encontrado para producto {item.producto_id}")

        pu = orig.precio_unitario
        di = getattr(orig, 'descuento_individual', 0.0)
        # 4.2) Calcular subtotal de devolución con descuento_individual
        sub = pu * item.cantidad * (1 - di/100)

        detalle = devol_models.DetalleDevolucion(
            devolucion_id         = nueva_dev.id,
            producto_id           = item.producto_id,
            cantidad              = item.cantidad,
            precio_unitario       = pu,
            descuento_individual  = di,
            subtotal              = sub
        )
        db.add(detalle)

        # 4.3) Ajustar stock (solo si reponer_stock es True)
        if data.reponer_stock:
            producto = db.query(productos_models.Producto).filter(
                productos_models.Producto.id == item.producto_id
            ).first()
            if not producto:
                raise ValueError(f"Producto {item.producto_id} no encontrado")
            producto.stock_actual = (producto.stock_actual or 0) + item.cantidad
            db.add(producto)

    # 5) Guardar todo
    db.commit()
    db.refresh(nueva_dev)
    return nueva_dev


def update_devolucion(db: Session, devolucion_id: int, data: DevolucionCreate) -> devol_models.Devolucion:
    """
    Actualiza una devolución, revierte stock antiguo, valida límites,
    y crea nuevos detalles respetando precio y descuentos individuales.
    """
    devol = db.query(devol_models.Devolucion).filter(
        devol_models.Devolucion.id == devolucion_id
    ).first()
    if not devol:
        raise ValueError("Devolución no encontrada")

    # 1) Revertir stock y borrar detalles previos
    # Solo revertimos (restamos lo devuelto) si la devolución anterior había repuesto stock.
    if devol.reponer_stock:
        for detalle in devol.detalles:
            prod = db.query(productos_models.Producto).filter(
                productos_models.Producto.id == detalle.producto_id
            ).first()
            if prod:
                prod.stock_actual = (prod.stock_actual or 0) - detalle.cantidad
                db.add(prod)
    
    # Borrar detalles viejos
    for detalle in devol.detalles:
        db.delete(detalle)
    db.flush()

    # Actualizamos el flag en la cabecera
    devol.reponer_stock = data.reponer_stock
    devol.detalle = data.detalle
    db.add(devol)

    # 2) Validar nuevo límite de devolución
    for item in data.items:
        sold_qty = db.query(func.coalesce(func.sum(dv_models.DetalleVenta.cantidad), 0)).filter(
            dv_models.DetalleVenta.venta_id == devol.venta_id,
            dv_models.DetalleVenta.producto_id == item.producto_id
        ).scalar() or 0
        returned_qty = db.query(func.coalesce(func.sum(devol_models.DetalleDevolucion.cantidad), 0)).join(
            devol_models.Devolucion
        ).filter(
            devol_models.Devolucion.venta_id == devol.venta_id,
            devol_models.DetalleDevolucion.producto_id == item.producto_id
        ).scalar() or 0
        if returned_qty + item.cantidad > sold_qty:
            disp = sold_qty - returned_qty
            raise ValueError(
                f"No puedes devolver {item.cantidad} unidades del producto {item.producto_id}; "
                f"solo quedan {disp} disponibles"
            )

    # 3) Crear nuevos detalles con precio y descuento
    for item in data.items:
        orig = (
            db.query(dv_models.DetalleVenta)
            .filter(
                dv_models.DetalleVenta.venta_id == devol.venta_id,
                dv_models.DetalleVenta.producto_id == item.producto_id
            )
            .first()
        )
        if not orig:
            raise ValueError(f"Detalle de venta no encontrado para producto {item.producto_id}")

        pu = orig.precio_unitario
        di = getattr(orig, 'descuento_individual', 0.0)
        sub = pu * item.cantidad * (1 - di/100)

        nuevo_detalle = devol_models.DetalleDevolucion(
            devolucion_id         = devol.id,
            producto_id           = item.producto_id,
            cantidad              = item.cantidad,
            precio_unitario       = pu,
            descuento_individual  = di,
            subtotal              = sub
        )
        db.add(nuevo_detalle)

        db.add(nuevo_detalle)

        if data.reponer_stock:
            prod = db.query(productos_models.Producto).filter(
                productos_models.Producto.id == item.producto_id
            ).first()
            prod.stock_actual = (prod.stock_actual or 0) + item.cantidad
            db.add(prod)

    db.commit()
    db.refresh(devol)
    return devol

def get_all_devoluciones(db: Session) -> list[devol_models.Devolucion]:
    """
    Devuelve todas las devoluciones registradas.
    """
    return db.query(devol_models.Devolucion).order_by(devol_models.Devolucion.fecha.desc(), devol_models.Devolucion.id.desc()).all()


def get_devolucion_by_id(db: Session, devolucion_id: int) -> devol_models.Devolucion | None:
    """
    Obtiene una devolución por su ID.
    """
    return db.query(devol_models.Devolucion).filter(
        devol_models.Devolucion.id == devolucion_id
    ).first()
    
def delete_devolucion(db: Session, devolucion_id: int) -> None:
    """
    Elimina una devolución y ajusta el stock_actual.
    """
    devol = db.query(devol_models.Devolucion).filter(
        devol_models.Devolucion.id == devolucion_id
    ).first()
    if not devol:
        raise ValueError("Devolución no encontrada")

    # Revertir stock_actual (si aplicaba) y eliminar detalles
    if devol.reponer_stock:
        for detalle in devol.detalles:
            producto = db.query(productos_models.Producto).filter(
                productos_models.Producto.id == detalle.producto_id
            ).first()
            if producto:
                producto.stock_actual = (producto.stock_actual or 0) - detalle.cantidad
                db.add(producto)

    db.query(devol_models.DetalleDevolucion).filter(
        devol_models.DetalleDevolucion.devolucion_id == devolucion_id
    ).delete()
    db.delete(devol)
    db.commit()