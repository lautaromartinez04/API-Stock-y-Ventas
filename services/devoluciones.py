from sqlalchemy.orm import Session
from sqlalchemy import func
import models.devoluciones as devol_models
import models.ventas as ventas_models
import models.productos as productos_models
import models.detalle_venta as dv_models
from schemas.devoluciones import DevolucionCreate


def create_devolucion(db: Session, data: DevolucionCreate) -> devol_models.Devolucion:
    """
    Crea una devolución y sus detalles asociados, valida límites,
    y actualiza el stock_actual de los productos.
    """
    venta = db.query(ventas_models.Venta).filter(
        ventas_models.Venta.id == data.venta_id
    ).first()
    if not venta:
        raise ValueError("Venta no encontrada")

    # Validar para cada ítem que no exceda lo vendido
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

    # Crear devolución
    nueva_dev = devol_models.Devolucion(venta_id=data.venta_id)
    db.add(nueva_dev)
    db.flush()

    # Crear detalles y ajustar stock_actual
    for item in data.items:
        detalle = devol_models.DetalleDevolucion(
            devolucion_id=nueva_dev.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad
        )
        db.add(detalle)
        producto = db.query(productos_models.Producto).filter(
            productos_models.Producto.id == item.producto_id
        ).first()
        if not producto:
            raise ValueError(f"Producto {item.producto_id} no encontrado")
        producto.stock_actual = (producto.stock_actual or 0) + item.cantidad
        db.add(producto)

    db.commit()
    db.refresh(nueva_dev)
    return nueva_dev


def get_all_devoluciones(db: Session) -> list[devol_models.Devolucion]:
    """
    Devuelve todas las devoluciones registradas.
    """
    return db.query(devol_models.Devolucion).all()


def get_devolucion_by_id(db: Session, devolucion_id: int) -> devol_models.Devolucion | None:
    """
    Obtiene una devolución por su ID.
    """
    return db.query(devol_models.Devolucion).filter(
        devol_models.Devolucion.id == devolucion_id
    ).first()


def update_devolucion(db: Session, devolucion_id: int, data: DevolucionCreate) -> devol_models.Devolucion:
    """
    Actualiza una devolución, valida límites y ajusta el stock_actual.
    """
    devol = db.query(devol_models.Devolucion).filter(
        devol_models.Devolucion.id == devolucion_id
    ).first()
    if not devol:
        raise ValueError("Devolución no encontrada")

    # Revertir stock_actual antiguo y eliminar detalles
    for detalle in devol.detalles:
        producto = db.query(productos_models.Producto).filter(
            productos_models.Producto.id == detalle.producto_id
        ).first()
        if producto:
            producto.stock_actual = (producto.stock_actual or 0) - detalle.cantidad
            db.add(producto)
        db.delete(detalle)
    db.flush()

    # Validar nuevos detalles
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
            disponible = sold_qty - returned_qty
            raise ValueError(
                f"No puedes devolver {item.cantidad} unidades del producto {item.producto_id}; "
                f"solo quedan {disponible} disponibles"
            )

    # Crear nuevos detalles y ajustar stock_actual
    for item in data.items:
        nuevo_detalle = devol_models.DetalleDevolucion(
            devolucion_id=devol.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad
        )
        db.add(nuevo_detalle)
        producto = db.query(productos_models.Producto).filter(
            productos_models.Producto.id == item.producto_id
        ).first()
        producto.stock_actual = (producto.stock_actual or 0) + item.cantidad
        db.add(producto)

    db.commit()
    db.refresh(devol)
    return devol


def delete_devolucion(db: Session, devolucion_id: int) -> None:
    """
    Elimina una devolución y ajusta el stock_actual.
    """
    devol = db.query(devol_models.Devolucion).filter(
        devol_models.Devolucion.id == devolucion_id
    ).first()
    if not devol:
        raise ValueError("Devolución no encontrada")

    # Revertir stock_actual y eliminar detalles
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