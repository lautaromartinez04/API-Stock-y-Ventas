from fastapi import APIRouter, status, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.database import get_db
from models.productos import Producto as ProductoModel
from schemas.producto import Producto, ProductoCreate
from services.productos import ProductoService
from middlewares.jwt_bearer import JWTBearer
from pathlib import Path

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
        raise HTTPException(status_code=404, detail="No encontrado")
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
    precio_unitario: float = Form(...),
    categoria_id: int = Form(1),
    activo: bool = Form(True),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    service = ProductoService(db)
    image_url = None
    if file:
        if file.content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(status_code=400, detail="Solo JPEG o PNG")
        filename = f"{codigo}_{Path(file.filename).name}"
        filepath = UPLOAD_DIR / filename
        with filepath.open("wb") as f:
            f.write(await file.read())
        image_url = f"/uploads/{filename}"

    nuevo = ProductoCreate(
        nombre=nombre,
        codigo=codigo,
        descripcion=descripcion,
        stock_actual=stock_actual,
        precio_unitario=precio_unitario,
        categoria_id=categoria_id,
        activo=activo,
        image_url=image_url,
    )
    return service.create(nuevo)

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
    precio_unitario: float = Form(None),
    categoria_id: int = Form(None),
    activo: bool = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    service = ProductoService(db)
    prod = service.get(id)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    update_data = prod.model_dump()
    if nombre is not None: update_data['nombre'] = nombre
    if codigo is not None: update_data['codigo'] = codigo
    if descripcion is not None: update_data['descripcion'] = descripcion
    if stock_actual is not None: update_data['stock_actual'] = stock_actual
    if precio_unitario is not None: update_data['precio_unitario'] = precio_unitario
    if categoria_id is not None: update_data['categoria_id'] = categoria_id
    if activo is not None: update_data['activo'] = activo

    updated = service.update(id, ProductoCreate(**update_data))
    if file:
        if file.content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(status_code=400, detail="Solo JPEG o PNG")
        filename = f"{id}_{Path(file.filename).name}"
        filepath = UPLOAD_DIR / filename
        with filepath.open("wb") as f:
            f.write(await file.read())
        image_url = f"/uploads/{filename}"
        updated = service.set_image(id, image_url)

    return updated

@productos_router.delete(
    "/productos/{id}",
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())]
)
def delete_producto(id: int, db: Session = Depends(get_db)):
    ProductoService(db).delete(id)
    return JSONResponse(status_code=200, content={"message": "Se ha eliminado el producto"})

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
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Solo JPEG o PNG")

    filename = f"{id}_{Path(file.filename).name}"
    filepath = UPLOAD_DIR / filename
    with filepath.open("wb") as f:
        f.write(await file.read())
    image_url = f"/uploads/{filename}"
    return service.set_image(id, image_url)