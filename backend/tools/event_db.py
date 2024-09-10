import json
from . import google_calendar

cal = google_calendar.GoogleCalendar()
cal.authenticate()

events = cal.read_events()["events"]
with open("events.json", "w") as f:
    json.dump(events, f, indent=4)

from openai import OpenAI

client = OpenAI(api_key=open("openai_key.txt", "r").read())

assistant = client.beta.assistants.create(
    name="Calendar Assistant",
    instructions="You are a calendar helper",
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)

# Create a vector store caled "Financial Statements"
vector_store = client.beta.vector_stores.create(name="Events")



# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=[open("events.json", "rb")]
)

# You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)
