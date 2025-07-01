from models.detalle_venta import DetalleVenta as DetalleVentaModel
from schemas.detalle_venta import DetalleVentaCreate, DetalleVenta

class DetalleVentaService:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        result = self.db.query(DetalleVentaModel).all()
        return [DetalleVenta.model_validate(d) for d in result]

    def create(self, detalle: DetalleVentaCreate):
        new_detalle = DetalleVentaModel(**detalle.dict())
        self.db.add(new_detalle)
        self.db.commit()
        self.db.refresh(new_detalle)
        return new_detalle

    def get(self, id: int):
        result = self.db.query(DetalleVentaModel).filter(DetalleVentaModel.id == id).first()
        return DetalleVenta.model_validate(result)

    def update(self, id: int, detalle: DetalleVentaCreate):
        result = self.db.query(DetalleVentaModel).filter(DetalleVentaModel.id == id).first()
        if not result:
            return None
        for key, value in detalle.dict().items():
            setattr(result, key, value)
        self.db.commit()
        self.db.refresh(result)
        return result

    def delete(self, id: int):
        self.db.query(DetalleVentaModel).filter(DetalleVentaModel.id == id).delete()
        self.db.commit()
