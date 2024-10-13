import uuid
from database.firebase_db import FirebaseDBManager


class DataManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db_manager = FirebaseDBManager()
        self.local_cache = self._default_data()
        self.cloud_updates = []  # Accumulates cloud updates

    def load_cache_from_cloud(self):
        self.local_cache = self.db_manager.create_or_get_user(
            self.user_id, self._default_data()
        )

    def _default_data(self):
        return {"chat": [], "events": [], "todo": []}

    def get_user_data(self):
        return self.local_cache

    def _update_local(self, field, data):
        """Updates the local cache and queues the update for the cloud."""
        self.local_cache[field] = data
        self._queue_cloud_update("update", field, data)

    def _append_to_local(self, field, data):
        """Appends data to the local cache and queues the update for the cloud."""
        self.local_cache[field].append(data)
        self._queue_cloud_update("append", field, data)

    def _queue_cloud_update(self, method, field, data):
        """Accumulates cloud update requests to be applied later."""
        self.cloud_updates.append((method, field, data))

    def apply_cloud_updates(self):
        """Applies all accumulated cloud updates to the cloud."""
        for method, field, data in self.cloud_updates:
            if method == "update":
                self.db_manager.update_user_field(self.user_id, field, data)
            elif method == "append":
                self.db_manager.append_to_array_field(self.user_id, field, data)
        self.cloud_updates.clear()  # Clear the updates after applying

    # Chat management
    def get_chat(self):
        return self.local_cache["chat"]

    def append_chat_message(self, message):
        self._append_to_local("chat", message)

    # Events management
    def get_events(self):
        return self.local_cache["events"]

    def add_event(self, event):
        self._append_to_local("events", event)

    def remove_event(self, event_id):
        # More efficient event removal without saving all non-removed events to the cloud right away
        updated_events = [
            event for event in self.local_cache["events"] if event["id"] != event_id
        ]
        self._update_local("events", updated_events)

    # Todo management with randomly generated ID
    def get_todo_list(self):
        return self.local_cache["todo"]

    def add_todo_item(self, task, deadline, category):
        todo_item = {
            "id": str(uuid.uuid4()),
            "task": task,
            "deadline": deadline,
            "category": category,
        }
        self._append_to_local("todo", todo_item)

    def remove_todo_item(self, todo_id):
        # Efficient removal of a specific todo item
        updated_todo = [
            todo for todo in self.local_cache["todo"] if todo["id"] != todo_id
        ]
        self._update_local("todo", updated_todo)
