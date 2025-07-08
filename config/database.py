from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session as SessionType
from typing import Generator

DATABASE_URL = "mysql+mysqlconnector://root:310501@localhost:3306/tienda"

# 1) Engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 2) Fábrica de sesiones YA ligadas al engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# 3) Base para tus modelos
Base = declarative_base()

# 4) Dependency para inyectar sesión
def get_db() -> Generator[SessionType, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
