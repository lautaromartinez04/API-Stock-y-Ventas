from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config.database import engine, Base
from middlewares.error_handler import ErrorHandler

# Routers
from routers.usuarios import usuarios_router
from routers.productos import productos_router
from routers.categorias import categorias_router
from routers.clientes import clientes_router
from routers.ventas import ventas_router
from routers.detalle_venta import detalle_ventas_router
from routers.ws import ws_router
from routers.devoluciones import devoluciones_router

app = FastAPI(
    title="API de Ventas y Stock",
    version="1.0.0"
)

# Montar carpeta de uploads para servir imágenes
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

# Middleware de manejo de errores
app.add_middleware(ErrorHandler)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(usuarios_router)
app.include_router(productos_router)
app.include_router(categorias_router)
app.include_router(clientes_router)
app.include_router(ventas_router)
app.include_router(detalle_ventas_router)
app.include_router(ws_router)
app.include_router(devoluciones_router)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

@app.get("/", tags=["home"])
def message():
    return HTMLResponse("<h1>API de Control de Ventas, Stock y Devoluciones</h1>")
