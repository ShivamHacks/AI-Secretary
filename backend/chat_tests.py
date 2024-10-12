import unittest
import json
import pprint
from datetime import datetime, timedelta
from tools.cached_google_calendar import CachedGoogleCalendar
from tools.task_manager import TaskManager
from chat import Chat
from tools import utils



class TestAISecretaryReal(unittest.TestCase):

    def setUp(self):
        print(f"\nRunning test: {self._testMethodName}\n")
        self.chat = Chat(user_id="test_user")

        # TEMPORARY - clear db until don't actually update DB
        #self.chat.data_manager._update_local_and_cloud("chat", self.chat.data_manager.get_chat()[0])
        self.chat.data_manager._update_local_and_cloud("events", [])
        self.chat.data_manager._update_local_and_cloud("todo", [])

    @unittest.skip("Works, can prevent skipping later")
    def test_add_event(self):
        message = "add an hour for coffee today at 6pm"
        list(self.chat.stream_message_response(message))
        print(self.chat.data_manager.get_chat()[-1])

        self.assertEqual(
            len(self.chat.google_calendar.list_cached_events()),
            1,
            f"Created more than one event:\n{pprint.pformat(self.chat.google_calendar.list_cached_events())}",
        )
        coffee_event = self.chat.google_calendar.list_cached_events()[0]
        self.assertIsNotNone(coffee_event, "No new 'coffee' event was found")
        event_start_time = datetime.strptime(
            utils.from_rfc3339(coffee_event["start"]["dateTime"]), utils.DATE_STRING_FMT
        )
        self.assertEqual(
            event_start_time.date(),
            datetime.now().date(),
            "Event is not scheduled for today",
        )
        self.assertEqual(event_start_time.hour, 18, "Event is not at 6 PM")

    def test_update_event_when_not_in_chat_history(self):
        message = "move my evening coffee to 7pm"
        # Add coffee from 6 - 7 to calendar
        start_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        coffee_event = self.chat.google_calendar.create_event(
            datetime.strftime(start_time, utils.DATE_STRING_FMT), datetime.strftime(end_time, utils.DATE_STRING_FMT), "Coffee"
        )

        list(self.chat.stream_message_response(message))
        print(self.chat.data_manager.get_chat()[-1])

        self.assertEqual(
            len(self.chat.google_calendar.pending_operations),
            2,
            f"Should only have create and update operation:\n{pprint.pformat(self.chat.google_calendar.list_cached_events())}",
        )
        print(self.chat.google_calendar.pending_operations[1])
        operation_name, event_id, operation = self.chat.google_calendar.pending_operations[1]
        self.assertEqual(operation_name, "update", f"Not an operation update: {operation}")
        self.assertEqual(event_id, coffee_event["event"]["id"], "Not updating the right event")


    @unittest.skip("Doesn't work for now")
    def test_delete_event_when_not_in_chat_history(self):
        delete_message = f"delete the event '{self.temp_event['summary']}'"
        response = list(self.chat.stream_message_response(delete_message))
        print("Got response for deleting event:", json.dumps(response)[:100] + "...")

        events_after = self.chat.google_calendar.read_events()["events"]
        deleted_event = next(
            (event for event in events_after if event["id"] == self.temp_event_id), None
        )
        self.assertIsNone(deleted_event, "Event was not deleted")


if __name__ == "__main__":
    unittest.main()
