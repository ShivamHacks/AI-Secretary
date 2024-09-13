import json
import copy
from openai import OpenAI

client = OpenAI(api_key=open("openai_key.txt", "r").read())
with open("local_data_example.json", "r") as file:
    example_data = json.load(file)

class Chat:

    def __init__(self, user_id):
        self.user_id = user_id
        self.user_data = copy.deepcopy(example_data)

    def handle_message(self, message):
        self.user_data["chat"].extend(
            [
                {"role": "user", "content": message},
                {"role": "assistant", "content": f'You said "{message}"'},
            ]
        )
    
    def get_data(self):
        return self.user_data
