import unittest
import json
import pprint
from datetime import datetime, timedelta
from tools.cached_google_calendar import CachedGoogleCalendar
from tools.task_manager import TaskManager
from chat import Chat
from tools import utils
import uuid


class TestAISecretaryReal(unittest.TestCase):

    def setUp(self):
        print(f"\nRunning test: {self._testMethodName}")
        self.chat = Chat(user_id="test_user")

    def test_add_event(self):
        message = "add an hour for coffee today at 6pm"
        list(self.chat.stream_message_response(message))

        self.assertEqual(
            len(self.chat.google_calendar.list_cached_events()),
            1,
            f"Created more than one event:\n{pprint.pformat(self.chat.google_calendar.list_cached_events())}",
        )
        coffee_event = self.chat.google_calendar.list_cached_events()[0]
        self.assertTrue(
            "coffee" in coffee_event["summary"].lower(),
            "No new 'coffee' event was found",
        )
        self.assertEqual(
            coffee_event["start"]["dateTime"].date(),
            datetime.now().date(),
            "Event is not scheduled for today",
        )
        self.assertEqual(
            coffee_event["start"]["dateTime"].hour, 18, "Event is not at 6 PM"
        )

    def test_update_event_empty_chat_history(self):
        message = "move my evening coffee to 7pm"
        # Add coffee from 6 - 7 to calendar
        start_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        original_event = self.chat.google_calendar.create_event(
            datetime.strftime(start_time, utils.DATE_STRING_FMT),
            datetime.strftime(end_time, utils.DATE_STRING_FMT),
            "Coffee",
        )["event"]

        list(self.chat.stream_message_response(message))

        self.assertEqual(
            len(self.chat.google_calendar.list_cached_events()),
            1,
            f"Should only have one event:\n{pprint.pformat(self.chat.google_calendar.list_cached_events())}",
        )
        updated_event = self.chat.google_calendar.list_cached_events()[0]
        self.assertEqual(original_event["id"], updated_event["id"], "IDs do not match")
        self.assertEqual(
            updated_event["start"]["dateTime"],
            datetime.now().replace(hour=19, minute=0, second=0, microsecond=0),
            "Did not update time correctly",
        )

    def test_delete_event_empty_chat_history(self):
        message = "remove my coffee for today"
        # Add coffee from 6 - 7 to calendar
        start_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        original_event = self.chat.google_calendar.create_event(
            datetime.strftime(start_time, utils.DATE_STRING_FMT),
            datetime.strftime(end_time, utils.DATE_STRING_FMT),
            "Coffee",
        )["event"]

        list(self.chat.stream_message_response(message))

        self.assertEqual(
            len(self.chat.google_calendar.list_cached_events()),
            0,
            f"Calendar should be empty",
        )

    def test_create_task(self):
        message = "create a task to finish the report by tomorrow"
        list(self.chat.stream_message_response(message))

        tasks = self.chat.data_manager.get_cache("todo")
        self.assertEqual(len(tasks), 1, "Should have one task created")
        task = tasks[0]
        self.assertTrue("report" in task["task"].lower(), "Task is not about report")
        self.assertEqual(
            task["deadline"],
            utils.string_from_date(datetime.now() + timedelta(days=1)),
            "Task due date is not set to tomorrow",
        )

    def test_update_task_empty_chat_history(self):
        self.chat.task_manager.create_task(
            "Finish the report", "work", utils.string_from_date(datetime.now())
        )
        update_message = "actually I need to finish the report a week later"
        list(self.chat.stream_message_response(update_message))

        tasks = self.chat.data_manager.get_cache("todo")
        self.assertEqual(len(tasks), 1, "Should have one task updated")
        task = tasks[0]
        self.assertEqual(
            utils.date_from_string(task["deadline"]).date(),
            (datetime.now() + timedelta(days=7)).date(),
            "Task due date not moved a week later",
        )

    def test_delete_task_empty_chat_history(self):
        self.chat.task_manager.create_task(
            "Finish the report", "work", utils.string_from_date(datetime.now())
        )
        update_message = "I don't need to do the report anymore"
        list(self.chat.stream_message_response(update_message))

        tasks = self.chat.data_manager.get_cache("todo")
        self.assertEqual(len(tasks), 0, "There shouldn't be any tasks")


if __name__ == "__main__":
    unittest.main()
