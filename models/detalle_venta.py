from sqlalchemy import Column, Integer, Float, ForeignKey
from config.database import Base

class DetalleVenta(Base):
    __tablename__ = "detalle_ventas"

    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Float, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    descuento_individual = Column(Float, nullable=False)
    costo_unitario = Column(Float, default=0) # Nuevo campo para costo histórico
