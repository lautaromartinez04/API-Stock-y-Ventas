# routers/ws.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from utils.connection_manager import manager
from utils.jwt_manager import validate_token

ws_router = APIRouter()

@ws_router.websocket("/ws/ventas")
async def websocket_ventas(ws: WebSocket):
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        validate_token(token)
    except:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(ws, "ventas")
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws, "ventas")


@ws_router.websocket("/ws/stock")
async def websocket_stock(ws: WebSocket):
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        validate_token(token)
    except:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(ws, "stock")
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws, "stock")
