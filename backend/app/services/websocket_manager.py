import asyncio
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.connections.discard(websocket)

    async def broadcast_incident(self, incident: dict) -> None:
        payload = {"event": "incident.updated", "incident": incident}
        failed = []
        for connection in self.connections.copy():
            try:
                await connection.send_json(payload)
            except Exception:
                failed.append(connection)
        for connection in failed:
            self.disconnect(connection)


manager = ConnectionManager()
