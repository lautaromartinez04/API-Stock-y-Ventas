# models/gastos.py

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from config.database import Base
from datetime import datetime

class Gasto(Base):
    __tablename__ = "gastos"

    id          = Column(Integer, primary_key=True, index=True)
    fecha       = Column(DateTime, nullable=False, default=datetime.utcnow)
    monto       = Column(Float, nullable=False)
    descripcion = Column(String(255), nullable=True)
    usuario_id  = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
