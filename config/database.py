from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+mysqlconnector://root:310501@localhost:3306/tienda"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Dependencia de FastAPI para obtener una sesión de DB y cerrarla automáticamente.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
