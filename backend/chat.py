import json
import copy
from openai import OpenAI
from tools.google_calendar import GoogleCalendar

client = OpenAI(api_key=open("openai_key.txt", "r").read())
with open("local_data_example.json", "r") as file:
    example_data = json.load(file)

system_prompt = """
You are an AI secretary and life coach. You help your user organize their
calendar and ensure they are reaching their goals.
"""

FAKE_CHAT = False


class Chat:

    def __init__(self, user_id):
        self.user_id = user_id
        if FAKE_CHAT:
            self.user_data = copy.deepcopy(example_data)
        else:
            self.user_data = {
                "chat": [
                    {"role": "system", "content": system_prompt}
                ],
                "events": [],
                "todo": []
            }
        self.google_calendar = GoogleCalendar()
        self.google_calendar.authenticate()

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
            tools=self.google_calendar.get_tool_metadata()
        )

        # TODO: this is not thread safe
        self.user_data["chat"].append({
            "role": "assistant",
            "content": ""
        })

        partial_function_calls = {}
        
        for chunk in stream:
            # Check if there are tool calls in the current chunk
            if chunk.choices[0].delta.tool_calls is not None:
                for tool_call in chunk.choices[0].delta.tool_calls:
                    print(tool_call)
                    index = tool_call.index
                    if index not in partial_function_calls:
                        # Initialize the structure for a new function call
                        partial_function_calls[index] = {
                            "name": tool_call.function.name,
                            "arguments": "",
                            "tool_call_id": tool_call.id
                        }
                    
                    # Accumulate the arguments
                    partial_function_calls[index]["arguments"] += tool_call.function.arguments

                    # Check if the arguments are complete (in this case, by detecting a closing brace)
                    if partial_function_calls[index]["arguments"].endswith('"}'):
                        # We assume the function call is now complete
                        completed_function_call = partial_function_calls.pop(index)
                        function_name = completed_function_call["name"]
                        function_arguments = completed_function_call["arguments"]
                        function_call_id = completed_function_call["tool_call_id"]

                        # Create the function call message
                        function_call_message = {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": function_call_id,
                                    "type": "function",
                                    "function": {
                                        "arguments": json.dumps(function_arguments),
                                        "name": function_name
                                    }
                                }
                            ]
                        }

                        # Append the function call message to the conversation
                        self.user_data["chat"].append(function_call_message)
                        
                        # Process the function call (e.g., execute it)
                        print(f"Executing function '{function_name}' with arguments: {function_arguments}")
                        
                        # Execute your function here using function_name and function_arguments
                        result = self.google_calendar.process_function_call(function_name, function_arguments)
                        function_call_result_message = {
                            "role": "tool",
                            "content": json.dumps(result),
                            "tool_call_id": function_call_id
                        }

                        # Append this result to the conversation
                        self.user_data["chat"].append(function_call_result_message)

                        # TODO: make it stream and use tools
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=self.user_data["chat"]
                        )
                        print(response)
                        self.user_data["chat"].append({
                            "role": "assistant",
                            "content": response.choices[0].message.content
                        })

                        # Yield updated user data if needed
                        yield self.user_data

            if chunk.choices[0].delta.content is not None:
                self.user_data["chat"][-1]["content"] += chunk.choices[0].delta.content
                # Stream full data because the chat might modify events and todo
                # list while running a single query through function calling
                yield self.user_data

    def get_data(self):
        return self.user_data
