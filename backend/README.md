# Running

App: `python app.py`
Server: `uvicorn server:app --reload`

Tests:
* `python -m tools.google_calendar_test`

Architectural changes to make
- use objects everywhere, e.g. Chat instance has chat, events, todo. Then Event has id, start, etc. Also same for communicating between server and frontend. Start is a datetime.
  then these objects can have the necessary conversions from string and all. Right now I'm running into dict key missing
  errors, JSON serialization to give to GPT, and difficult to refactor fields.
- topical logging. E.g. event CRUD, DB CRUD, ...
- better error logging in a privacy safe way

Smaller refactorings
- calendar cache should use database cache? same for todo list