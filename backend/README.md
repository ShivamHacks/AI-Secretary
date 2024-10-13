# Running

App: `python app.py`
Server: `uvicorn server:app --reload`

Tests:
* `python -m tools.google_calendar_test`
* `python -m unittest chat_tests.TestAISecretaryReal.test_create_task`

Architectural changes to make
- use objects everywhere, e.g. Chat instance has chat, events, todo. Then Event has id, start, etc. Also same for communicating between server and frontend. Start is a datetime.
  then these objects can have the necessary conversions from string and all. Right now I'm running into dict key missing
  errors, JSON serialization to give to GPT, and difficult to refactor fields.
- topical logging. E.g. event CRUD, DB CRUD, ...
- better error logging in a privacy safe way

Smaller refactorings
- calendar cache should use database cache? same for todo list

Latency
- anytime the local cache changes, push to client so it feels snappy

UX
- add messaging dots so users know message was received

Refresh server

1. `ssh ec2-user@ec2-3-141-106-24.us-east-2.compute.amazonaws.com`
2. `cd AI-Secretary`
3. `git pull origin main`
4. `cd backend `
5. `source .venv/bin/activate`
6. `pip install -r requirements.txt`
7. `./run.sh`

To send any local credential files:

`scp <file> ec2-user@ec2-3-141-106-24.us-east-2.compute.amazonaws.com:<path>`
