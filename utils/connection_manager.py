from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_stock: List[WebSocket] = []
        self.active_sales: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel == "stock":
            self.active_stock.append(websocket)
        else:
            self.active_sales.append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        lst = self.active_stock if channel == "stock" else self.active_sales
        lst.remove(websocket)

    async def broadcast(self, message: dict, channel: str):
        lst = self.active_stock if channel == "stock" else self.active_sales
        for ws in lst:
            await ws.send_json(message)

# ¡Aquí creamos la instancia única!
manager = ConnectionManager()
