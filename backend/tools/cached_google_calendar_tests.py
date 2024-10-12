import unittest
from unittest.mock import patch, MagicMock
import uuid
import json

from cached_google_calendar import CachedGoogleCalendar
import utils
from datetime import datetime, timedelta


class TestCachedGoogleCalendar(unittest.TestCase):

    def setUp(self):
        self.calendar = CachedGoogleCalendar()

    @patch.object(CachedGoogleCalendar, "authenticate_locally")
    @patch.object(CachedGoogleCalendar, "read_events_to_cache")
    @patch.object(CachedGoogleCalendar, "sync_with_google_calendar")
    def test_create_event(self, mock_sync, mock_read, mock_auth):
        # Test data
        start_date_time = utils.now_plus_hours(0)
        end_date_time = utils.now_plus_hours(1)
        summary = "Test Event"

        # Call the method
        result = self.calendar.create_event(start_date_time, end_date_time, summary)

        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["event"]["summary"], summary)
        self.assertEqual(
            result["event"]["start"]["dateTime"], utils.to_rfc3339(start_date_time)
        )
        self.assertEqual(
            result["event"]["end"]["dateTime"], utils.to_rfc3339(end_date_time)
        )
        self.assertEqual(len(self.calendar.cache), 1)  # One event in cache
        self.assertEqual(
            len(self.calendar.pending_operations), 1
        )  # One pending operation

    @patch.object(CachedGoogleCalendar, "authenticate_locally")
    @patch.object(CachedGoogleCalendar, "read_events_to_cache")
    @patch.object(CachedGoogleCalendar, "sync_with_google_calendar")
    def test_update_event(self, mock_sync, mock_read, mock_auth):
        # Add an event first
        event_id = str(uuid.uuid4())
        self.calendar.cache.append(
            {
                "id": event_id,
                "summary": "Old Event",
                "start": {
                    "dateTime": utils.to_rfc3339(utils.now_plus_hours(0)),
                    "timeZone": "America/Los_Angeles",
                },
                "end": {
                    "dateTime": utils.to_rfc3339(utils.now_plus_hours(2)),
                    "timeZone": "America/Los_Angeles",
                },
            }
        )

        # Update the event
        new_summary = "Updated Event"
        new_start_date_time = utils.now_plus_hours(6)
        new_end_date_time = utils.now_plus_hours(10)
        result = self.calendar.update_event(
            event_id, new_summary, new_start_date_time, new_end_date_time
        )

        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(self.calendar.cache[0]["summary"], new_summary)
        self.assertEqual(
            self.calendar.cache[0]["start"]["dateTime"],
            utils.to_rfc3339(new_start_date_time),
        )
        self.assertEqual(
            self.calendar.cache[0]["end"]["dateTime"],
            utils.to_rfc3339(new_end_date_time),
        )
        self.assertEqual(len(self.calendar.pending_operations), 1)  # One pending update

    @patch.object(CachedGoogleCalendar, "authenticate_locally")
    @patch.object(CachedGoogleCalendar, "read_events_to_cache")
    @patch.object(CachedGoogleCalendar, "sync_with_google_calendar")
    def test_delete_event(self, mock_sync, mock_read, mock_auth):
        # Add an event to delete
        event_id = str(uuid.uuid4())
        self.calendar.cache.append(
            {
                "id": event_id,
                "summary": "Test Event",
                "start": {
                    "dateTime": utils.now_plus_hours(3),
                    "timeZone": "America/Los_Angeles",
                },
                "end": {
                    "dateTime": utils.now_plus_hours(5),
                    "timeZone": "America/Los_Angeles",
                },
            }
        )

        # Delete the event
        result = self.calendar.delete_event(event_id)

        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(len(self.calendar.cache), 0)  # Event removed from cache
        self.assertEqual(len(self.calendar.pending_operations), 1)  # One pending delete

    @patch.object(CachedGoogleCalendar, "authenticate_locally")
    @patch.object(CachedGoogleCalendar, "read_events_to_cache")
    @patch.object(CachedGoogleCalendar, "sync_with_google_calendar")
    def test_list_cached_events(self, mock_sync, mock_read, mock_auth):
        # Add some events to the cache
        self.calendar.cache = [
            {
                "id": str(uuid.uuid4()),
                "summary": "Event 1",
                "start": {
                    "dateTime": utils.now_plus_hours(3),
                    "timeZone": "America/Los_Angeles",
                },
                "end": {
                    "dateTime": utils.now_plus_hours(6),
                    "timeZone": "America/Los_Angeles",
                },
            },
            {
                "id": str(uuid.uuid4()),
                "summary": "Event 2",
                "start": {
                    "dateTime": utils.now_plus_hours(5),
                    "timeZone": "America/Los_Angeles",
                },
                "end": {
                    "dateTime": utils.now_plus_hours(8),
                    "timeZone": "America/Los_Angeles",
                },
            },
        ]

        # List events
        cached_events = self.calendar.list_cached_events()

        # Assertions
        self.assertEqual(len(cached_events), 2)
        self.assertEqual(cached_events[0]["summary"], "Event 1")
        self.assertEqual(cached_events[1]["summary"], "Event 2")

    @patch.object(CachedGoogleCalendar, "create_event")
    @patch.object(CachedGoogleCalendar, "update_event")
    @patch.object(CachedGoogleCalendar, "delete_event")
    @unittest.skip("Doesn't work for now")
    def test_process_function_calls(self, mock_delete, mock_update, mock_create):
        # Simulating function calls for create, update, and delete
        mock_create.return_value = {"success": True, "event": {"id": "temp123"}}
        mock_update.return_value = {"success": True}
        mock_delete.return_value = {"success": True}

        function_calls = [
            {
                "id": str(uuid.uuid4()),
                "function": {
                    "name": "calendar_create_event",
                    "arguments": json.dumps(
                        {
                            "summary": "New Event",
                            "start_date_time": "2024-10-10T10:00:00",
                            "end_date_time": "2024-10-10T11:00:00",
                        }
                    ),
                },
            },
            {
                "id": str(uuid.uuid4()),
                "function": {
                    "name": "calendar_update_event",
                    "arguments": json.dumps(
                        {"event_id": "temp123", "new_summary": "Updated Event"}
                    ),
                },
            },
            {
                "id": str(uuid.uuid4()),
                "function": {
                    "name": "calendar_delete_event",
                    "arguments": json.dumps({"event_id": "temp123"}),
                },
            },
        ]

        # Process function calls
        results = self.calendar.process_function_calls(function_calls)

        # Assertions
        mock_create.assert_called_once_with(
            start_date_time="2024-10-10T10:00:00",
            end_date_time="2024-10-10T11:00:00",
            summary="New Event",
        )
        mock_update.assert_called_once_with(
            event_id="temp123",
            new_summary="Updated Event",
            new_start_date_time=None,
            new_end_date_time=None,
        )
        mock_delete.assert_called_once_with(event_id="temp123")

        # Check that the results contain success responses for each function call
        self.assertEqual(len(results), 3)
        self.assertEqual(
            results[0]["output"], str({"success": True, "event": {"id": "temp123"}})
        )
        self.assertEqual(results[1]["output"], str({"success": True}))
        self.assertEqual(results[2]["output"], str({"success": True}))


if __name__ == "__main__":
    unittest.main()
