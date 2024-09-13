import json
import copy
from openai import OpenAI

client = OpenAI(api_key=open("openai_key.txt", "r").read())
with open("local_data_example.json", "r") as file:
    example_data = json.load(file)

FAKE_CHAT = False


class Chat:

    def __init__(self, user_id):
        self.user_id = user_id
        self.user_data = copy.deepcopy(example_data)

    def get_chat_response(self):
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            # TODO: might run over limit for chat history
            messages=self.user_data["chat"],
            stream=True,
        )

    def stream_message_response(self, message):
        self.user_data["chat"].append({
            "role": "user",
            "content": message
        })

        if FAKE_CHAT:
            self.user_data["chat"].append({
                "role": "assistant",
                "content": f'You said "{message}"'
            })
            return self.user_data

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.user_data["chat"],
            stream=True,
        )
        # TODO: this is not thread safe
        self.user_data["chat"].append({
            "role": "assistant",
            "content": ""
        })
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                self.user_data["chat"][-1]["content"] += chunk.choices[0].delta.content
                # Stream full data because the chat might modify events and todo
                # list while running a single query through function calling
                yield self.user_data

    def get_data(self):
        return self.user_data
