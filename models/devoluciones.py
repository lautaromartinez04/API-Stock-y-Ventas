from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from config.database import Base

class Devolucion(Base):
    __tablename__ = "devoluciones"
    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())

    # relación a los detalles de devolución
    detalles = relationship("DetalleDevolucion", back_populates="devolucion")


class DetalleDevolucion(Base):
    __tablename__ = "devoluciones_detalle"
    id = Column(Integer, primary_key=True, index=True)
    devolucion_id = Column(Integer, ForeignKey("devoluciones.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)

    devolucion = relationship("Devolucion", back_populates="detalles")
