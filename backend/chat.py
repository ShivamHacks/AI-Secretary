import json
import copy
from datetime import datetime
from openai import OpenAI
from tools.google_calendar import GoogleCalendar
from tools import utils

client = OpenAI(api_key=open("openai_key.txt", "r").read())
with open("local_data_example.json", "r") as file:
    example_data = json.load(file)

system_prompt = """
You are an AI secretary and life coach. You help your user organize their
calendar and todo list so that they are reaching their goals. Provide the
response without using any Markdown formatting like bold or italics. Be
concise. If the user asks for help, provide a brief explanation of the tool.
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
            self.update_events()

    def get_data(self):
        return self.user_data
    
    """
    The time needs to be updated in the conversation history to ensure that the
    conversation is up-to-date with the current time. This is important for
    tools that require the current time, such as scheduling events in the calendar.
    """
    def update_time_in_conversation(self):
        now = datetime.now().strftime(utils.DATE_STRING_FMT)
        self.user_data["chat"].append({
            "role": "system",
            "content": f"Today's date and time is {now}"
        })

    def update_events(self):
        events_response = self.google_calendar.read_events()
        if events_response["success"]:
            self.user_data["events"] = events_response["events"]

    def stream_message_response(self, message):
        self.update_time_in_conversation()

        # Step 1: Handle user input
        self._add_user_message(message)

        # Step 2: Fake chat for testing
        if FAKE_CHAT:
            self._add_fake_response(message)
            return self.user_data

        # Step 3: Start the streaming process
        stream = self._initialize_stream()
        yield from self._yield_from_stream(stream)

    def _add_user_message(self, message):
        self.user_data["chat"].append({
            "role": "user",
            "content": message
        })

    def _add_fake_response(self, message):
        self.user_data["chat"].append({
            "role": "assistant",
            "content": f'You said "{message}"'
        })

    def _initialize_stream(self):
        self.user_data["chat"].append({
            "role": "assistant",
            "content": ""
        })
        return client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.user_data["chat"],
            stream=True,
            tools=self.google_calendar.get_tool_metadata()
        )
    
    def _yield_from_stream(self, stream):
        # Step 4: Placeholder for incomplete function calls
        partial_function_calls = {}

        for chunk in stream:
            # Step 5: Process tool calls if present
            if chunk.choices[0].delta.tool_calls is not None:
                yield from self._process_tool_calls(chunk, partial_function_calls)

            # Step 6: Handle real-time content streaming
            if chunk.choices[0].delta.content is not None:
                self.user_data["chat"][-1]["content"] += chunk.choices[0].delta.content
                yield self.user_data

        # TODO: only update events if something changed, and that too only the changed part
        self.update_events()
        yield self.user_data


    def _process_tool_calls(self, chunk, partial_function_calls):
        for tool_call in chunk.choices[0].delta.tool_calls:
            print(tool_call)
            index = tool_call.index
            # Create new function call
            if index not in partial_function_calls:
                partial_function_calls[index] = {
                    "name": tool_call.function.name,
                    "arguments": "",
                    "tool_call_id": tool_call.id
                }
            partial_function_calls[index]["arguments"] += tool_call.function.arguments

            if partial_function_calls[index]["arguments"].endswith('"}'):
                completed_function_call = partial_function_calls.pop(index)
                self._handle_complete_function_call(completed_function_call)

                # Continue stream
                stream = self._initialize_stream()
                yield from self._yield_from_stream(stream)

    def _handle_complete_function_call(self, completed_function_call):
        function_name = completed_function_call["name"]
        function_arguments = json.loads(completed_function_call["arguments"])
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
        self.user_data["chat"].append(function_call_message)

        # Execute the function
        result = self.google_calendar.process_function_call(function_name, function_arguments)

        # Create the result message
        function_call_result_message = {
            "role": "tool",
            "content": json.dumps(result),
            "tool_call_id": function_call_id
        }
        self.user_data["chat"].append(function_call_result_message)
    