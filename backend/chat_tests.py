import unittest
import json
from datetime import datetime, timedelta
from tools.google_calendar import GoogleCalendar
from tools.task_manager import TaskManager
from chat import Chat
from tools import utils


class TestAISecretaryReal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.calendar = GoogleCalendar()
        cls.calendar.authenticate(api_creds_path="google_creds.json")
        cls.chat = Chat(user_id="real_user")
        cls.chat.google_calendar = cls.calendar
        cls.chat.task_manager = TaskManager([])

    def setUp(self):
        self.events_before = self.chat.google_calendar.read_events()["events"]

    def test_add_event_evening(self):
        message = "add time for coffee today in the evening"
        response = list(self.chat.stream_message_response(message))
        print("Got response:", json.dumps(response)[:100] + "...")

        events_after = self.chat.google_calendar.read_events()["events"]
        new_events = [
            event for event in events_after if event not in self.events_before
        ]
        print("Created new events:", json.dumps(new_events)[:100] + "...")

        coffee_event = None
        for event in new_events:
            if "coffee" in event.get("summary", "").lower():
                coffee_event = event
                break

        # Verify the event exists and is in the evening (after 6 PM)
        self.assertIsNotNone(coffee_event, "No new 'coffee' event was found")
        event_start_time = datetime.strptime(
            coffee_event["start"], utils.DATE_STRING_FMT
        )
        self.assertEqual(
            event_start_time.date(),
            datetime.now().date(),
            "Event is not scheduled for today",
        )
        self.assertGreaterEqual(event_start_time.hour, 18, "Event is not after 6 PM")
        self.assertLess(event_start_time.hour, 24, "Event is not before midnight")

    def tearDown(self):
        # Cleanup: Delete only the new events added during the test
        events_after = self.chat.google_calendar.read_events()["events"]
        new_events = [
            event for event in events_after if event not in self.events_before
        ]
        for event in new_events:
            self.chat.google_calendar.delete_event(event["id"])


if __name__ == "__main__":
    unittest.main()
