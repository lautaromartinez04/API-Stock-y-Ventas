from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from config.database import Base

class Producto(Base):
    __tablename__ = "productos"

    id              = Column(Integer, primary_key=True)
    nombre          = Column(String(100), nullable=False)
    codigo          = Column(String(50), unique=True, nullable=False)
    descripcion     = Column(String(255), nullable=True)

    # Stock y alerta individual
    stock_actual    = Column(Integer, default=0, nullable=False)
    stock_bajo      = Column(Integer, default=5, nullable=False)

    # Costo, margen y precio de venta
    precio_costo    = Column(Float, default=0.0, nullable=False)    # Precio de costo
    margen          = Column(Float, default=25.0, nullable=False)   # Margen deseado (%)  
    precio_unitario = Column(Float, nullable=False)                 # Precio de venta

    categoria_id    = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    activo          = Column(Boolean, default=True, nullable=False)
    image_url       = Column(String(255), nullable=True)
