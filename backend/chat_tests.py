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

    def test_add_event_evening(self):
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
        self.assertGreaterEqual(event_start_time.hour, 18, "Event is not after 6 PM")
        self.assertLess(event_start_time.hour, 24, "Event is not before midnight")

    @unittest.skip("Doesn't work for now")
    def test_update_event_when_not_in_chat_history(self):
        update_message = f"update the event '{self.temp_event['summary']}' to 'Updated Temporary Event'"
        response = list(self.chat.stream_message_response(update_message))
        print("Got response for updating event:", json.dumps(response)[:100] + "...")

        events_after = self.chat.google_calendar.read_events()["events"]
        updated_event = next(
            (event for event in events_after if event["id"] == self.temp_event_id), None
        )
        self.assertIsNotNone(updated_event, "Updated event not found")
        self.assertEqual(
            updated_event["summary"],
            "Updated Temporary Event",
            "Event summary was not updated",
        )

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
