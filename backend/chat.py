import json
from datetime import datetime, timedelta
from openai import OpenAI
from tools.cached_google_calendar import CachedGoogleCalendar
from tools.task_manager import TaskManager
from tools import utils
from database.cached_cloud_db import DataManager  # Import your DataManager class

"""
Bugs:
- right now returns from yield for each function call. Try adding 3 tasks at once and responds multiple times:
^ yea, this message also led to a lot of repeat calls:
"So right now it's about 12:30 and I want to get a few things done by 12:30. It's really important that I work out, and I am feeling good for that. That will take about an hour. I also want to call family for about an hour. I also want to demo my product to Dipesh. I'll also need to meal prep, but that can only happen after 5pm when I get my grocieres. And i'm meeting a friend for dinner at 6pm so all this needs to get done before"
"I've got a few admin things I need to do. I need to open the chase mail by next Tuesday, and do my laundry tomorrow. Can you add this to my todo list?"

"""

client = OpenAI(api_key=open("openai_key.txt", "r").read())
system_prompt = """
You are an AI secretary and life coach. You help your user organize their
calendar and todo list so that they are reaching their goals. Provide the
response without using any Markdown formatting like bold or italics. Be
concise. If the user asks for help, provide a brief explanation of the tool.
"""


class Chat:

    def __init__(self, user_id):
        self.user_id = user_id
        self.data_manager = DataManager(user_id)
        self.google_calendar = CachedGoogleCalendar(self.data_manager)
        self.task_manager = TaskManager(self.data_manager)

        # If the chat is empty, i.e. new user, then add the system prompt
        # TODO: find better way to do this
        if len(self.data_manager.get_chat()) == 0:
            self.data_manager.append_chat_message(
                {"role": "system", "content": system_prompt}
            )

    def get_data(self):
        return self.data_manager.get_user_data()

    def load_from_database(self):
        self.data_manager.load_cache_from_cloud()
    
    def set_access_token(self, access_token):
        self.google_calendar.set_access_token(access_token)

    def load_calendar(self):
        self.google_calendar.read_events_to_cache()

    def update_time_in_conversation(self):
        """
        The time needs to be updated in the conversation history to ensure that the
        conversation is up-to-date with the current time. This is important for
        tools that require the current time, such as scheduling events in the calendar.
        """
        now = datetime.now().strftime(utils.DATE_STRING_FMT)
        # Append time to chat using DataManager
        self.data_manager.append_chat_message(
            {"role": "system", "content": f"Today's date and time is {now}"}
        )

    def add_relevant_context_to_chat(self):
        """
        Adds relevant context like previous week and next 2 weeks of events and full task
        list. This should eventually be replaced with RAG.
        """
        message = ""

        start_date = (datetime.now() - timedelta(days=7)).strftime(
            utils.DATE_STRING_FMT
        )
        end_date = (datetime.now() + timedelta(days=14)).strftime(utils.DATE_STRING_FMT)
        relevant_events = self.google_calendar.read_events(start_date, end_date)[
            "events"
        ]
        if len(relevant_events) != 0:
            events_table = "ID\t\tStart\tEnd\t\tEvent\n"
            events_table += "-" * 50 + "\n"
            for event in relevant_events:
                id = event["id"]
                start = utils.string_from_date(event["start"]["dateTime"])
                end = utils.string_from_date(event["end"]["dateTime"])
                summary = event["summary"]
                events_table += f"{id}\t{start}\t{end}\t{summary}\n"
            
            message += f"The last 7 days and next 14 days worth of events are:\n{events_table}\n"

        todo_list = self.data_manager.get_cache("todo")
        if len(todo_list) > 0:
            todo_table = "ID\t\Task\tDeadline\t\tCategoru\n"
            todo_table += "-" * 50 + "\n"
            for item in todo_list:
                id = item["id"]
                task = item["task"]
                deadline = item["deadline"]
                category = item["category"]
                todo_table += f"{id}\t{task}\t{deadline}\t{category}\n"
            
            message += f"The todo list is:\n{todo_table}"
        
        if message == "":
            return

        self.data_manager.append_chat_message(
            {
                "role": "system",
                "content": message,
            }
        )

    def stream_message_response(self, message):
        self.update_time_in_conversation()
        self.add_relevant_context_to_chat()
        self._add_user_message(message)
        stream = self._initialize_stream()
        yield from self._yield_from_stream(stream)

    def _add_user_message(self, message):
        self.data_manager.append_chat_message({"role": "user", "content": message})

    def _initialize_stream(self):
        return client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.data_manager.get_chat(),
            stream=True,
            tools=self.google_calendar.get_tool_metadata()
            + self.task_manager.get_tool_metadata(),
        )

    def _yield_from_stream(self, stream):
        partial_function_calls = {}
        streamed_response = ""

        for chunk in stream:
            # Tool calls
            if chunk.choices[0].finish_reason == "tool_calls":
                for index, function_call in partial_function_calls.items():
                    # HACK
                    if index != 0:
                        continue
                    self._handle_complete_function_call(function_call)

                    # need to start new stream because function calls done
                    yield from self._yield_from_stream(self._initialize_stream())
            if chunk.choices[0].delta.tool_calls is not None:
                self._process_tool_calls(chunk, partial_function_calls)

            # Real time content streaming
            if chunk.choices[0].delta.content is not None:
                streamed_response += chunk.choices[0].delta.content
                yield {"type": "chunk", "chunk": chunk.choices[0].delta.content}

        # TODO: only update events if something changed, and that too only the changed part
        self.data_manager.append_chat_message(
            {"role": "assistant", "content": streamed_response}
        )

    def _process_tool_calls(self, chunk, partial_function_calls):
        for tool_call in chunk.choices[0].delta.tool_calls:
            index = tool_call.index

            # Create new function call
            if index not in partial_function_calls:
                partial_function_calls[index] = {
                    "name": tool_call.function.name,
                    "arguments": "",
                    "tool_call_id": tool_call.id,
                }
            partial_function_calls[index]["arguments"] += tool_call.function.arguments

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
                        "name": function_name,
                    },
                }
            ],
        }
        self.data_manager.append_chat_message(function_call_message)

        # Determine which tool to use based on the function name prefix
        if function_name.startswith("calendar_"):
            result = self.google_calendar.process_function_call(
                function_name, function_arguments
            )
        elif function_name.startswith("task_"):
            result = self.task_manager.process_function_call(
                function_name, function_arguments
            )
        else:
            print(f"Unknown function name prefix for function: {function_name}")
            return

        # Create the result message
        function_call_result_message = {
            "role": "tool",
            "content": json.dumps(result, cls=utils.DateTimeEncoder),
            "tool_call_id": function_call_id,
        }
        self.data_manager.append_chat_message(function_call_result_message)
