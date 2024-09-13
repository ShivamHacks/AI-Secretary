from fastapi import FastAPI, WebSocket
import json
import copy
from chat import Chat

app = FastAPI()

user_data = {
    "user1": Chat("user1"),
}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global user_data
    current_user = "user1"
    await websocket.accept()

    # Send the initial data to the client
    await websocket.send_text(json.dumps(user_data[current_user].get_data()))

    while True:
        # Wait for the client to send a message
        data = await websocket.receive_text()
        try:
            received_message = json.loads(data)
            print(received_message)
            if "newMessage" in received_message:
                new_message = received_message["newMessage"]
                user_data[current_user].handle_message(new_message)

            if "changeUser" in received_message:
                current_user = received_message["changeUser"]
                if current_user in user_data:
                    print(f"Setting user to existing user {current_user}")
                else:
                    print(f"Creating new data for {current_user}")
                    user_data[current_user] = Chat(current_user)

            # Send the updated data back to the client
            await websocket.send_text(json.dumps(user_data[current_user].get_data()))

        except json.JSONDecodeError:
            await websocket.send_text("Error: Invalid JSON format received.")
