import unittest
from unittest.mock import patch, mock_open
import json
from types import SimpleNamespace
from calendar_manager import CalendarManager


class TestCalendarManager(unittest.TestCase):
    def setUp(self):
        self.mock_open_patcher = patch(
            "builtins.open", new_callable=mock_open, read_data="[]"
        )
        self.mock_open = self.mock_open_patcher.start()
        self.calendar_manager = CalendarManager(file_name="test_calendar.txt")

    def tearDown(self):
        self.mock_open_patcher.stop()

    def test_load_calendar(self):
        self.calendar_manager.load_calendar()
        self.assertEqual(self.calendar_manager.events, [])

    def test_save_calendar(self):
        self.calendar_manager.events = [
            {
                "id": "1",
                "name": "Test Event",
                "start_date": "2024-07-27",
                "end_date": "2024-07-27",
                "start_time": "10:00",
                "end_time": "11:00",
            }
        ]
        self.calendar_manager.save_calendar()
        self.mock_open().write.assert_called_once_with(
            json.dumps(self.calendar_manager.events, default=str)
        )

    def test_create_event(self):
        result = self.calendar_manager.create_event(
            "Meeting", "2024-07-27", "2024-07-27", "10:00", "11:00"
        )
        self.assertTrue(result["success"])
        self.assertIn("event", result)
        self.assertEqual(result["event"]["name"], "Meeting")

    def test_read_events(self):
        self.calendar_manager.events = [
            {
                "id": "1",
                "name": "Test Event",
                "start_date": "2024-07-27",
                "end_date": "2024-07-27",
                "start_time": "10:00",
                "end_time": "11:00",
            },
            {
                "id": "2",
                "name": "Another Event",
                "start_date": "2024-08-01",
                "end_date": "2024-08-01",
                "start_time": "12:00",
                "end_time": "13:00",
            },
        ]
        events = self.calendar_manager.read_events("2024-07-01", "2024-07-31")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["name"], "Test Event")

    def test_modify_event(self):
        self.calendar_manager.events = [
            {
                "id": "1",
                "name": "Test Event",
                "start_date": "2024-07-27",
                "end_date": "2024-07-27",
                "start_time": "10:00",
                "end_time": "11:00",
            }
        ]
        result = self.calendar_manager.modify_event(
            "1", new_name="Updated Event", new_start_date="2024-07-28"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["event"]["name"], "Updated Event")
        self.assertEqual(result["event"]["start_date"], "2024-07-28")

    def test_delete_event(self):
        self.calendar_manager.events = [
            {
                "id": "1",
                "name": "Test Event",
                "start_date": "2024-07-27",
                "end_date": "2024-07-27",
                "start_time": "10:00",
                "end_time": "11:00",
            }
        ]
        result = self.calendar_manager.delete_event("1")
        self.assertTrue(result["success"])
        self.assertEqual(result["event_id"], "1")
        self.assertEqual(len(self.calendar_manager.events), 0)

    def test_get_tool_metadata(self):
        metadata = self.calendar_manager.get_tool_metadata()
        self.assertIsInstance(metadata, list)
        self.assertGreater(len(metadata), 0)

    def test_process_function_calls(self):
        function_calls = [
            SimpleNamespace(
                id="call_1",
                function=SimpleNamespace(
                    arguments='{"start_date": "2024-07-01", "end_date": "2024-07-31"}',
                    name="calendar_read_events",
                ),
                type="function",
            ),
            SimpleNamespace(
                id="call_2",
                function=SimpleNamespace(
                    arguments='{"name": "Workshop", "start_date": "2024-09-01", "end_date": "2024-09-01", "start_time": "14:00", "end_time": "16:00"}',
                    name="calendar_create_event",
                ),
                type="function",
            ),
        ]

        results = self.calendar_manager.process_function_calls(function_calls)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["tool_call_id"], "call_1")
        self.assertIn("output", results[0])
        self.assertEqual(results[1]["tool_call_id"], "call_2")
        self.assertIn("output", results[1])


if __name__ == "__main__":
    unittest.main()
