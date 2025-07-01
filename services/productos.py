from models.productos import Producto as ProductoModel
from schemas.producto import ProductoCreate, Producto

class ProductoService:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        result = self.db.query(ProductoModel).all()
        return [Producto.model_validate(p) for p in result]

    def create(self, producto: ProductoCreate):
        new_producto = ProductoModel(**producto.dict())
        self.db.add(new_producto)
        self.db.commit()
        self.db.refresh(new_producto)
        return new_producto

    def get(self, id: int):
        result = self.db.query(ProductoModel).filter(ProductoModel.id == id).first()
        return Producto.model_validate(result)

    def update(self, id: int, producto: ProductoCreate):
        result = self.db.query(ProductoModel).filter(ProductoModel.id == id).first()
        if not result:
            return None
        for key, value in producto.dict().items():
            setattr(result, key, value)
        self.db.commit()
        self.db.refresh(result)
        return result

    def delete(self, id: int):
        self.db.query(ProductoModel).filter(ProductoModel.id == id).delete()
        self.db.commit()
