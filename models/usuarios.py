from sqlalchemy import Column, Integer, String

from config.database import Base

class Usuarios(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable=False)  # Solo username
    password = Column(String(1000), nullable=False)  # Solo password
