from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from config.database import Session
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
def get_productos():
    db = Session()
    return ProductoService(db).get_all()

@productos_router.get(
    "/productos/{id}",
    response_model=Producto,
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())]
)
def get_producto(id: int):
    db = Session()
    prod = ProductoService(db).get(id)
    if not prod:
        raise HTTPException(status_code=404, detail="No encontrado")
    return prod

@productos_router.post(
    "/productos",
    response_model=Producto,
    status_code=201,
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())]
)
def create_producto(producto: ProductoCreate):
    db = Session()
    return ProductoService(db).create(producto)

@productos_router.put(
    "/productos/{id}",
    response_model=Producto,
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())]
)
def update_producto(id: int, producto: ProductoCreate):
    db = Session()
    updated = ProductoService(db).update(id, producto)
    if not updated:
        raise HTTPException(status_code=404, detail="No encontrado")
    return updated

@productos_router.delete(
    "/productos/{id}",
    tags=["Productos"],
    dependencies=[Depends(JWTBearer())]
)
def delete_producto(id: int):
    db = Session()
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
    file: UploadFile = File(...)
):
    # Validar producto
    db = Session()
    service = ProductoService(db)
    prod = service.get(id)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Validar tipo
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Solo JPEG o PNG")

    # Guardar en /uploads
    filename = f"{id}_{Path(file.filename).name}"
    filepath = UPLOAD_DIR / filename
    with filepath.open("wb") as f:
        f.write(await file.read())

    # Actualizar URL en BD
    image_url = f"/uploads/{filename}"
    updated = service.set_image(id, image_url)
    return updated
