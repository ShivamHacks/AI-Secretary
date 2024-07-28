from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler

client = OpenAI(api_key=open("openai_key.txt", "r").read())

instructions = """
You are an AI secretary and life coach. You help your user organize their
calendar and ensure they are reaching their goals.
"""

assistant = client.beta.assistants.create(
    name="AI Secretary",
    instructions=instructions,
    model="gpt-4o",
)

thread = client.beta.threads.create()


class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == "code_interpreter":
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

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

    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please address the user as Shivam Agrawal. Be very concise",
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

    print()
