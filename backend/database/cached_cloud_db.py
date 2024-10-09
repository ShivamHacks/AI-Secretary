import uuid
from database.firebase_db import FirebaseDBManager

class DataManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db_manager = FirebaseDBManager()        
        self.local_cache = self.db_manager.create_or_get_user(user_id, self._default_data())

    def _default_data(self):
        return {
            "chat": [],
            "events": [],
            "todo": []
        }

    def get_user_data(self):
        return self.local_cache

    def _update_local_and_cloud(self, field, data):
        self.local_cache[field] = data
        self.db_manager.update_user_field(self.user_id, field, data)

    def _append_to_local_and_cloud(self, field, data):
        self.local_cache[field].append(data)
        self.db_manager.append_to_array_field(self.user_id, field, data)

    # Chat management
    def get_chat(self):
        return self.local_cache["chat"]

    def append_chat_message(self, message):
        self._append_to_local_and_cloud("chat", message)

    # Events management
    def get_events(self):
        return self.local_cache["events"]

    def add_event(self, event):
        self._append_to_local_and_cloud("events", event)

    def remove_event(self, event_id):
        # TODO: make more efficient by only removing the specific item rather than saving all non-removed
        updated_events = [event for event in self.local_cache['events'] if event['id'] != event_id]
        self._update_local_and_cloud('events', updated_events)

    # Todo management with randomly generated ID
    def get_todo_list(self):
        return self.local_cache["todo"]

    def add_todo_item(self, task, deadline, category):
        todo_item = {
            "id": str(uuid.uuid4()),
            "task": task,
            "deadline": deadline,
            "category": category
        }
        self._append_to_local_and_cloud("todo", todo_item)

    def remove_todo_item(self, todo_id):
        # TODO: make more efficient by only removing the specific item rather than saving all non-removed
        updated_todo = [todo for todo in self.local_cache['todo'] if todo['id'] != todo_id]
        self._update_local_and_cloud('todo', updated_todo)
