# services/gastos.py

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.gastos import Gasto as GastoModel
from schemas.gasto import Gasto, GastoCreate

class GastoService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Gasto]:
        gastos = self.db.query(GastoModel).order_by(GastoModel.fecha.desc()).all()
        return [Gasto.model_validate(g) for g in gastos]

    def get(self, id: int) -> Gasto | None:
        g = self.db.query(GastoModel).filter(GastoModel.id == id).first()
        return Gasto.model_validate(g) if g else None

    def create(self, payload: GastoCreate) -> Gasto:
        gasto = GastoModel(
            monto       = payload.monto,
            descripcion = payload.descripcion,
            usuario_id  = payload.usuario_id
        )
        try:
            self.db.add(gasto)
            self.db.commit()
            self.db.refresh(gasto)
            return Gasto.model_validate(gasto)
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al crear el gasto"
            )

    def update(self, id: int, payload: GastoCreate) -> Gasto | None:
        gasto = self.db.query(GastoModel).filter(GastoModel.id == id).first()
        if not gasto:
            return None
        gasto.monto       = payload.monto
        gasto.descripcion = payload.descripcion
        gasto.usuario_id  = payload.usuario_id
        try:
            self.db.commit()
            self.db.refresh(gasto)
            return Gasto.model_validate(gasto)
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al actualizar el gasto"
            )

    def delete(self, id: int) -> None:
        self.db.query(GastoModel).filter(GastoModel.id == id).delete()
        self.db.commit()
