# src/models/venta.py

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Boolean
from sqlalchemy.sql import func
from config.database import Base

class Venta(Base):
    __tablename__ = "ventas"

    id                   = Column(Integer, primary_key=True)
    fecha                = Column(DateTime, default=func.now())
    total_sin_descuento  = Column(Float, nullable=False)     # bruto antes del descuento
    descuento            = Column(Float, default=0.0)        # porcentaje (0–100)
    total                = Column(Float, nullable=False)     # neto tras aplicar descuento
    cliente_id           = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    usuario_id           = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    forma_pago           = Column(String(20), nullable=False, default="efectivo")
    pagado               = Column(Boolean, nullable=False, default=False)
