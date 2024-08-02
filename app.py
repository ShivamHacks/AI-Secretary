from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler
# from tools.calendar_manager import CalendarManager
from tools.utils import *
from tools.google_calendar import GoogleCalendar
from datetime import datetime

client = OpenAI(api_key=open("openai_key.txt", "r").read())

instructions = """
You are an AI secretary and life coach. You help your user organize their
calendar and ensure they are reaching their goals.
"""

calendar_manager = GoogleCalendar()
calendar_manager.authenticate()

assistant = client.beta.assistants.create(
    name="AI Secretary",
    instructions=instructions,
    model="gpt-4o",
    tools=calendar_manager.get_tool_metadata(),
)

thread = client.beta.threads.create()


class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    @override
    def on_event(self, event):
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == "thread.run.requires_action":
            run_id = event.data.id  # Retrieve the run ID from the event data
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        tool_outputs = calendar_manager.process_function_calls(data.required_action.submit_tool_outputs.tool_calls)
        # Submit all tool_outputs at the same time
        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        # Use the submit_tool_outputs_stream helper
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()


quit_words = ["exit", "quit"]

while True:
    content = input("> ")

    if content == "":
        continue

    if content in quit_words:
        print("Closing")
        break

    message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=str(content)
    )

    # Inject current time
    now = datetime.now().strftime(DATE_STRING_FMT)
    print(now)

    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=f"Please address the user as Shivam Agrawal. Today's date is {now}. Be very concise",
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

    print()
