from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.productos import Producto as ProductoModel
from schemas.producto import Producto, ProductoCreate

class ProductoService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Producto]:
        prods = self.db.query(ProductoModel).all()
        return [Producto.model_validate(p) for p in prods]

    def get(self, id: int) -> Producto | None:
        prod = self.db.query(ProductoModel).filter(ProductoModel.id == id).first()
        return prod and Producto.model_validate(prod)

    def create(self, payload: ProductoCreate) -> Producto:
        try:
            # Validaciones básicas
            if payload.stock_bajo < 0:
                raise HTTPException(400, "stock_bajo no puede ser negativo")
            if payload.precio_costo < 0:
                raise HTTPException(400, "precio_costo no puede ser negativo")
            if payload.precio_unitario < payload.precio_costo:
                raise HTTPException(400, "precio_unitario debe ser ≥ precio_costo")

            # Recalcular margen
            margen = (
                (payload.precio_unitario - payload.precio_costo)
                / payload.precio_costo * 100
                if payload.precio_costo > 0 else 0.0
            )

            prod = ProductoModel(
                nombre          = payload.nombre,
                codigo          = payload.codigo,
                descripcion     = payload.descripcion,
                stock_actual    = payload.stock_actual,
                stock_bajo      = payload.stock_bajo,
                precio_costo    = payload.precio_costo,
                margen          = margen,
                precio_unitario = payload.precio_unitario,
                categoria_id    = payload.categoria_id,
                activo          = payload.activo,
                image_url       = payload.image_url,
            )
            self.db.add(prod)
            self.db.commit()
            self.db.refresh(prod)
            return Producto.model_validate(prod)

        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(500, "Error interno al crear el producto")

    def update(self, id: int, payload: ProductoCreate) -> Producto | None:
        prod = self.db.query(ProductoModel).filter(ProductoModel.id == id).first()
        if not prod:
            return None

        data = payload.model_dump(exclude_none=True)
        # Validar y recalcular
        new_costo = data.get("precio_costo", prod.precio_costo)
        new_precio = data.get("precio_unitario", prod.precio_unitario)
        if new_costo < 0:
            raise HTTPException(400, "precio_costo no puede ser negativo")
        if new_precio < new_costo:
            raise HTTPException(400, "precio_unitario debe ser ≥ precio_costo")

        prod.precio_costo    = new_costo
        prod.precio_unitario = new_precio
        prod.margen = (
            (new_precio - new_costo) / new_costo * 100
            if new_costo > 0 else 0.0
        )

        if "stock_bajo" in data and data["stock_bajo"] < 0:
            raise HTTPException(400, "stock_bajo no puede ser negativo")

        # Actualizar el resto
        for fld in (
            "nombre", "codigo", "descripcion",
            "stock_actual", "stock_bajo",
            "categoria_id", "activo", "image_url"
        ):
            if fld in data:
                setattr(prod, fld, data[fld])

        try:
            self.db.commit()
            self.db.refresh(prod)
            return Producto.model_validate(prod)
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(500, "Error interno al actualizar el producto")

    def delete(self, id: int) -> None:
        self.db.query(ProductoModel).filter(ProductoModel.id == id).delete()
        self.db.commit()

    def set_image(self, id: int, image_url: str) -> Producto:
        prod = self.db.query(ProductoModel).filter(ProductoModel.id == id).first()
        if not prod:
            raise HTTPException(404, "Producto no encontrado")
        prod.image_url = image_url
        self.db.commit()
        self.db.refresh(prod)
        return Producto.model_validate(prod)
