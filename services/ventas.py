from models.ventas import Venta as VentaModel
from schemas.venta import VentaCreate, Venta

class VentaService:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        result = self.db.query(VentaModel).all()
        return [Venta.model_validate(v) for v in result]

    def create(self, venta: VentaCreate):
        new_venta = VentaModel(**venta.dict())
        self.db.add(new_venta)
        self.db.commit()
        self.db.refresh(new_venta)
        return new_venta

    def get(self, id: int):
        result = self.db.query(VentaModel).filter(VentaModel.id == id).first()
        return Venta.model_validate(result)

    def update(self, id: int, venta: VentaCreate):
        result = self.db.query(VentaModel).filter(VentaModel.id == id).first()
        if not result:
            return None
        for key, value in venta.dict().items():
            setattr(result, key, value)
        self.db.commit()
        self.db.refresh(result)
        return result

    def delete(self, id: int):
        self.db.query(VentaModel).filter(VentaModel.id == id).delete()
        self.db.commit()
