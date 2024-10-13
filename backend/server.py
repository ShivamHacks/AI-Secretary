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
        chat = self.user_data[user_id]
        chat.load_from_database()
        chat.load_calendar()

        await self.active_connections[user_id].send_text(
            json.dumps(
                {"type": "final", "data": chat.get_data()}, cls=utils.DateTimeEncoder
            )
        )

    async def handle_message(self, user_id: str, message: str):
        # Stream the message response back to the client
        chat = self.user_data[user_id]
        connection = self.active_connections[user_id]
        for chunk in chat.stream_message_response(message):
            await connection.send_text(json.dumps(chunk))

        # After the stream, upload all new data to cloud, pull updates from calendar, and send final data
        chat.data_manager.apply_cloud_updates()
        chat.google_calendar.sync_with_google_calendar()
        chat.load_calendar()
        await connection.send_text(
            json.dumps(
                {"type": "final", "data": chat.get_data()}, cls=utils.DateTimeEncoder
            )
        )

    async def send_feedback(self, user_id: str, feedback: str):
        chat = self.user_data[user_id]
        chat.data_manager.db_manager.send_feedback(user_id, feedback)
        connection = self.active_connections[user_id]
        await connection.send_text(
            json.dumps({"type": "feedback_confirmation", "feedback": feedback})
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

                # TODO: make this follow a proto or some object so parsing messages is cleaner
                if "newMessage" in received_message:
                    new_message = received_message["newMessage"]
                    await manager.handle_message(user_id, new_message)

                if "feedback" in received_message:
                    await manager.send_feedback(user_id, received_message["feedback"])

            except json.JSONDecodeError:
                await websocket.send_text("Error: Invalid JSON format received.")

    except WebSocketDisconnect:
        manager.disconnect(user_id)


@app.get("/")
def root():
    return f"Server up since {start_time.strftime(utils.DATE_STRING_FMT)}"
