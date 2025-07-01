from sqlalchemy import Column, Integer, String
from config.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    documento = Column(String(30), unique=True)
    direccion = Column(String(255))
    telefono = Column(String(30))
