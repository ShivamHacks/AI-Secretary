import json
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler
from tools import utils
from tools.google_calendar import GoogleCalendar
from datetime import datetime

client = OpenAI(api_key=open("openai_key.txt", "r").read())

instructions = """
You are an AI secretary and life coach. You help your user organize their
calendar and ensure they are reaching their goals.
"""

calendar_manager = GoogleCalendar()
calendar_manager.authenticate()

print("Adding events vector store")
events = calendar_manager.read_events()["events"]
with open("events.json", "w") as f:
    json.dump(events, f, indent=4)
vector_store = client.beta.vector_stores.create(name="Events")
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=[open("events.json", "rb")]
)

# TODO: add a general time tool to get the current time and date for multi-day sessions
tools = calendar_manager.get_tool_metadata()
tools.append({"type": "file_search"})

assistant = client.beta.assistants.create(
    name="AI Secretary",
    instructions=instructions,
    model="gpt-4o",
    tools=tools,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

HISTORY_FILE = "conversation_history.json"
LOAD_HISTORY = False
try:
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
        # Adding messages in the history seems to be limited to 32 messages
        # thread = client.beta.threads.create(messages=history)
        thread = client.beta.threads.create()
        if LOAD_HISTORY:
            print("Restoring message history", end="", flush=True)
            for message in history:
                print(".", end="", flush=True)
                message = client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role=message["role"],
                    content=message["content"],
                )
            print()

except FileNotFoundError:
    thread = client.beta.threads.create()
    history = []


class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    @override
    def on_text_done(self, text):
        history.append({"role": "assistant", "content": text.value})
        print()

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > tool call: {tool_call.type}\n", flush=True)

    @override
    def on_event(self, event):
        if event.event == "thread.run.requires_action":
            self.handle_requires_action(event.data)

    def handle_requires_action(self, data):
        tool_outputs = calendar_manager.process_function_calls(
            data.required_action.submit_tool_outputs.tool_calls
        )
        self.submit_tool_outputs(tool_outputs)

    def submit_tool_outputs(self, tool_outputs):
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()


quit_words = ["exit", "quit"]


def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


while True:
    content = input("> ")

    if content == "":
        continue

    if content in quit_words:
        print("Closing")
        save_history()
        break

    message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=str(content)
    )

    history.append({"role": "user", "content": str(content)})

    # Inject current time
    now = datetime.now().strftime(utils.DATE_STRING_FMT)

    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=f"Please address the user as Shivam Agrawal. Today's date is {now}. Be very concise.",
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

    save_history()
