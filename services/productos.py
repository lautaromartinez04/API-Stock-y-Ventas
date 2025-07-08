from fastapi import HTTPException
from models.productos import Producto as ProductoModel
from schemas.producto import ProductoCreate, Producto
from typing import List, Optional

class ProductoService:
    def __init__(self, db):
        self.db = db

    def get_all(self) -> List[Producto]:
        productos = self.db.query(ProductoModel).all()
        return [Producto.model_validate(p) for p in productos]

    def get(self, id: int) -> Optional[Producto]:
        prod = self.db.query(ProductoModel).filter(ProductoModel.id == id).first()
        if not prod:
            return None
        return Producto.model_validate(prod)

    def create(self, data: ProductoCreate) -> ProductoModel:
        new_prod = ProductoModel(**data.dict())
        self.db.add(new_prod)
        self.db.commit()
        self.db.refresh(new_prod)
        return new_prod

    def update(self, id: int, data: ProductoCreate) -> Optional[ProductoModel]:
        prod = self.db.query(ProductoModel).filter(ProductoModel.id == id).first()
        if not prod:
            return None
        for key, value in data.dict().items():
            setattr(prod, key, value)
        self.db.commit()
        self.db.refresh(prod)
        return prod

    def delete(self, id: int) -> None:
        self.db.query(ProductoModel).filter(ProductoModel.id == id).delete()
        self.db.commit()

    def set_image(self, id: int, image_url: str) -> ProductoModel:
        prod = self.db.query(ProductoModel).filter(ProductoModel.id == id).first()
        if not prod:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        prod.image_url = image_url
        self.db.commit()
        self.db.refresh(prod)
        return prod
