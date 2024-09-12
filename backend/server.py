from fastapi import FastAPI, WebSocket
import json

app = FastAPI()

with open("local_data_example.json", "r") as file:
    local_data = json.load(file)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Send the initial data to the client
    await websocket.send_text(json.dumps(local_data))
    while True:
        # Wait for the client to send a message
        data = await websocket.receive_text()
        try:
            received_message = json.loads(data)
            print(received_message)
            if "newMessage" in received_message:
                new_message = received_message["newMessage"]
                local_data["chat"].extend(
                    [
                        {"role": "user", "content": new_message},
                        {"role": "assistant", "content": f"You said {new_message}"},
                    ]
                )

                # Send the updated data back to the client
                await websocket.send_text(json.dumps(local_data))

        except json.JSONDecodeError:
            await websocket.send_text("Error: Invalid JSON format received.")
