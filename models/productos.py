
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from config.database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(255))
    stock_actual = Column(Integer, default=0)
    precio_unitario = Column(Float, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    activo = Column(Boolean, default=True)
    # Nuevo campo para almacenar la ruta/URL de la imagen
    image_url = Column(String(255), nullable=True)