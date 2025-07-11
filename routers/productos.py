from fastapi import APIRouter, status, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pathlib import Path

from config.database import get_db
from schemas.producto import Producto, ProductoCreate
from services.productos import ProductoService
from middlewares.jwt_bearer import JWTBearer

productos_router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@productos_router.get(
    "/productos",
    response_model=list[Producto],
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())]
)
def get_productos(db: Session = Depends(get_db)):
    return ProductoService(db).get_all()

@productos_router.get(
    "/productos/{id}",
    response_model=Producto,
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())]
)
def get_producto(id: int, db: Session = Depends(get_db)):
    prod = ProductoService(db).get(id)
    if not prod:
        raise HTTPException(404, "Producto no encontrado")
    return prod

@productos_router.post(
    "/productos",
    response_model=Producto,
    status_code=status.HTTP_201_CREATED,
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())]
)
async def create_producto(
    nombre: str = Form(...),
    codigo: str = Form(...),
    descripcion: str = Form(""),
    stock_actual: int = Form(0),
    stock_bajo: int = Form(5),
    precio_costo: float = Form(...),
    margen: float = Form(25.0),
    precio_unitario: float = Form(...),
    categoria_id: int = Form(None),
    activo: bool = Form(True),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    service = ProductoService(db)
    image_url = None
    if file:
        if file.content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(400, "Solo JPEG o PNG")
        name = f"{codigo}_{Path(file.filename).name}"
        path = UPLOAD_DIR / name
        with path.open("wb") as f:
            f.write(await file.read())
        image_url = f"/uploads/{name}"

    payload = ProductoCreate(
        nombre=nombre,
        codigo=codigo,
        descripcion=descripcion,
        stock_actual=stock_actual,
        stock_bajo=stock_bajo,
        precio_costo=precio_costo,
        precio_unitario=precio_unitario,
        categoria_id=categoria_id,
        activo=activo,
        image_url=image_url,
    )
    return service.create(payload)

@productos_router.put(
    "/productos/{id}",
    response_model=Producto,
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())]
)
async def update_producto(
    id: int,
    nombre: str = Form(None),
    codigo: str = Form(None),
    descripcion: str = Form(None),
    stock_actual: int = Form(None),
    stock_bajo: int = Form(None),
    precio_costo: float = Form(None),
    precio_unitario: float = Form(None),
    categoria_id: int = Form(None),
    activo: bool = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    service = ProductoService(db)
    existing = service.get(id)
    if not existing:
        raise HTTPException(404, "Producto no encontrado")

    data = existing.model_dump()
    for fld, val in [
        ("nombre", nombre), ("codigo", codigo), ("descripcion", descripcion),
        ("stock_actual", stock_actual), ("stock_bajo", stock_bajo),
        ("precio_costo", precio_costo), ("precio_unitario", precio_unitario),
        ("categoria_id", categoria_id), ("activo", activo),
    ]:
        if val is not None:
            data[fld] = val

    updated = service.update(id, ProductoCreate(**data))

    if file:
        if file.content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(400, "Solo JPEG o PNG")
        name = f"{id}_{Path(file.filename).name}"
        path = UPLOAD_DIR / name
        with path.open("wb") as f:
            f.write(await file.read())
        image_url = f"/uploads/{name}"
        updated = service.set_image(id, image_url)

    return updated

@productos_router.delete(
    "/productos/{id}",
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())]
)
def delete_producto(id: int, db: Session = Depends(get_db)):
    ProductoService(db).delete(id)
    return JSONResponse(status_code=200, content={"message": "Producto eliminado"})

@productos_router.post(
    "/productos/{id}/imagen",
    response_model=Producto,
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())]
)
async def upload_image(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    service = ProductoService(db)
    prod = service.get(id)
    if not prod:
        raise HTTPException(404, "Producto no encontrado")
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(400, "Solo JPEG o PNG")

    name = f"{id}_{Path(file.filename).name}"
    path = UPLOAD_DIR / name
    with path.open("wb") as f:
        f.write(await file.read())
    image_url = f"/uploads/{name}"
    return service.set_image(id, image_url)
