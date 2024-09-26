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
        print(f"\nRunning test: {self._testMethodName}\n")
        self.events_before = self.chat.google_calendar.read_events()["events"]
        self.tasks_before = self.chat.task_manager.task_list

        # Create a temporary event to use in the test where the chat history doesn't have context
        # This will be cleaned up in tearDown because it was added after storing the events_before
        start_time = (datetime.now() + timedelta(hours=1)).strftime(
            utils.DATE_STRING_FMT
        )
        end_time = (datetime.now() + timedelta(hours=2)).strftime(utils.DATE_STRING_FMT)
        response = self.chat.google_calendar.create_event(
            start_date_time=start_time,
            end_date_time=end_time,
            summary="Temporary Test Event",
        )

        self.assertTrue(response["success"], "Failed to create temporary event")
        self.temp_event = response["event"]
        self.temp_event_id = self.temp_event["id"]

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

    def test_delete_event_when_not_in_chat_history(self):
        delete_message = f"delete the event '{self.temp_event['summary']}'"
        response = list(self.chat.stream_message_response(delete_message))
        print("Got response for deleting event:", json.dumps(response)[:100] + "...")

        events_after = self.chat.google_calendar.read_events()["events"]
        deleted_event = next(
            (event for event in events_after if event["id"] == self.temp_event_id), None
        )
        self.assertIsNone(deleted_event, "Event was not deleted")

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
