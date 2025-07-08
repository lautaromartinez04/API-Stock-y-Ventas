from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal

from schemas.devoluciones import DevolucionCreate, DevolucionOut
from services.devoluciones import (
    create_devolucion,
    get_all_devoluciones,
    get_devolucion_by_id,
    update_devolucion,
    delete_devolucion
)

devoluciones_router = APIRouter(prefix="/devoluciones", tags=["Devoluciones"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@devoluciones_router.post("/", response_model=DevolucionOut, tags=["Devoluciones"])
def crear_dev(payload: DevolucionCreate, db: Session = Depends(get_db)):
    try:
        return create_devolucion(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@devoluciones_router.get("/", response_model=list[DevolucionOut], tags=["Devoluciones"])
def listar_devs(db: Session = Depends(get_db)):
    return get_all_devoluciones(db)

@devoluciones_router.get("/{id}", response_model=DevolucionOut)
def obtener_dev(id: int, db: Session = Depends(get_db)):
    dev = get_devolucion_by_id(db, id)
    if not dev:
        raise HTTPException(status_code=404, detail="Devolución no encontrada")
    return dev

@devoluciones_router.put("/{id}", response_model=DevolucionOut)
def editar_dev(id: int, payload: DevolucionCreate, db: Session = Depends(get_db)):
    try:
        return update_devolucion(db, id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@devoluciones_router.delete("/{id}", status_code=204)
def eliminar_dev(id: int, db: Session = Depends(get_db)):
    try:
        delete_devolucion(db, id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
