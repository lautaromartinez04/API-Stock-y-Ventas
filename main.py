from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from config.database import engine, Base
from middlewares.error_handler import ErrorHandler
from fastapi.middleware.cors import CORSMiddleware

# Routers
from routers.usuarios import usuarios_router
from routers.productos import productos_router
from routers.categorias import categorias_router
from routers.clientes import clientes_router
from routers.ventas import ventas_router
from routers.detalle_venta import detalle_ventas_router

app = FastAPI()
app.title = "API de Ventas y Stock"
app.version = "1.0.0"

app.add_middleware(ErrorHandler)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers
app.include_router(usuarios_router)
app.include_router(productos_router)
app.include_router(categorias_router)
app.include_router(clientes_router)
app.include_router(ventas_router)
app.include_router(detalle_ventas_router)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

@app.get("/", tags=["home"])
def message():
    return HTMLResponse("<h1>API de Control de Ventas y Stock</h1>")
