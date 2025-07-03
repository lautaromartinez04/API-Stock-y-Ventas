# routers/ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.connection_manager import ConnectionManager

ws_router = APIRouter()
manager = ConnectionManager()

@ws_router.websocket("/ws/stock")
async def websocket_stock(ws: WebSocket):
    await manager.connect(ws, "stock")
    try:
        while True:
            await ws.receive_text()  # opcional, si el cliente envía “ping”
    except WebSocketDisconnect:
        manager.disconnect(ws, "stock")

@ws_router.websocket("/ws/ventas")
async def websocket_ventas(ws: WebSocket):
    await manager.connect(ws, "ventas")
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws, "ventas")
