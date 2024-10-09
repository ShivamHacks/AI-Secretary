from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
import json
from datetime import datetime
from chat import Chat
from tools import utils

app = FastAPI()
start_time = datetime.now()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_data: Dict[str, Chat] = {}

    async def connect(self, websocket: WebSocket, user_id: str, access_token: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        if user_id not in self.user_data:
            self.user_data[user_id] = Chat(user_id)

        self.user_data[user_id].set_access_token(access_token)

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send_initial_data(self, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(
                json.dumps(
                    {"type": "final", "data": self.user_data[user_id].get_data()}
                )
            )

    async def handle_message(self, user_id: str, message: str):
        if user_id in self.user_data:
            # Stream the message response back to the client
            for chunk in self.user_data[user_id].stream_message_response(message):
                await self.active_connections[user_id].send_text(json.dumps(chunk))

            # After the stream, pull updates (Google Calendar, etc.) and send final updated data
            await self.active_connections[user_id].send_text(
                json.dumps(
                    {"type": "final", "data": self.user_data[user_id].get_data()}
                )
            )


manager = ConnectionManager()


@app.websocket("/ws/{user_id}/{access_token}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, access_token: str):
    try:
        await manager.connect(websocket, user_id, access_token)
        await manager.send_initial_data(user_id)

        while True:
            data = await websocket.receive_text()

            try:
                received_message = json.loads(data)

                if "newMessage" in received_message:
                    new_message = received_message["newMessage"]
                    await manager.handle_message(user_id, new_message)

            except json.JSONDecodeError:
                await websocket.send_text("Error: Invalid JSON format received.")

    except WebSocketDisconnect:
        manager.disconnect(user_id)


@app.get("/")
def root():
    return f"Server up since {start_time.strftime(utils.DATE_STRING_FMT)}"
