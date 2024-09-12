from fastapi import FastAPI, WebSocket
import json
import copy

app = FastAPI()

with open("local_data_example.json", "r") as file:
  local_data = json.load(file)

user_data = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  global user_data
  current_user = "user1"
  current_data = copy.deepcopy(local_data)
  await websocket.accept()

  # Send the initial data to the client
  await websocket.send_text(json.dumps(current_data))
  while True:
    # Wait for the client to send a message
    data = await websocket.receive_text()
    try:
      received_message = json.loads(data)
      print(received_message)
      if "newMessage" in received_message:
        new_message = received_message["newMessage"]
        current_data["chat"].extend(
          [
            {"role": "user", "content": new_message},
            {"role": "assistant", "content": f'You said "{new_message}"'},
          ]
        )

      if "changeUser" in received_message:
        user_data[current_user] = current_data
        new_user = received_message["changeUser"]
        current_user = new_user
        if new_user in user_data:
          print(f"Restoring data for {new_user}")
          current_data = user_data[new_user]
        else:
          print(f"Creating new data for {new_user}")
          current_data = copy.deepcopy(local_data)

      # Send the updated data back to the client
      await websocket.send_text(json.dumps(current_data))

    except json.JSONDecodeError:
      await websocket.send_text("Error: Invalid JSON format received.")
