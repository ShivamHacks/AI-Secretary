import unittest
from unittest.mock import patch, MagicMock
from .google_calendar import GoogleCalendar
from . import utils


class TestGoogleCalendar(unittest.TestCase):

    @patch("googleapiclient.discovery.build")
    @patch("builtins.input", return_value="Y")
    def test_create_event_user_confirmed(self, mock_input, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        gc = GoogleCalendar()
        gc.service = mock_service

        start_date_time = "2024-08-02 12:00 PM"
        end_date_time = "2024-08-02 2:00 PM"
        summary = "test event"

        result = gc.create_event(start_date_time, end_date_time, summary)

        self.assertTrue(result["success"])
        # TODO: verify the value of the event
        self.assertTrue(mock_service.events.return_value.insert.called)

    @patch("googleapiclient.discovery.build")
    @patch("builtins.input", return_value="n")
    def test_create_event_rejected(self, mock_input, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        gc = GoogleCalendar()
        gc.service = mock_service

        start_date_time = "2024-08-02 12:00 PM"
        end_date_time = "2024-08-02 2:00 PM"
        summary = "test event"

        result = gc.create_event(start_date_time, end_date_time, summary)

        self.assertEqual(result, utils.DEFAULT_USER_REJECTED_ACTION_MSG)
        self.assertFalse(mock_service.events.return_value.insert.called)

    @patch("googleapiclient.discovery.build")
    @patch("builtins.input", return_value="Y")
    def test_update_event_user_confirmed(self, mock_input, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        gc = GoogleCalendar()
        gc.service = mock_service

        event_id = "test_event_id"
        new_summary = "Updated Summary"
        new_start_date_time = "2024-08-02 3:00 PM"
        new_end_date_time = "2024-08-02 4:00 PM"

        mock_service.events.return_value.get.return_value.execute.return_value = {
            "id": event_id,
            "summary": "Old Summary",
            "start": {"dateTime": "2024-08-02T12:00:00-07:00"},
            "end": {"dateTime": "2024-08-02T14:00:00-07:00"},
        }

        result = gc.update_event(
            event_id, new_summary, new_start_date_time, new_end_date_time
        )

        self.assertTrue(result["success"])
        self.assertTrue(mock_service.events.return_value.update.called)

    @patch("googleapiclient.discovery.build")
    @patch("builtins.input", return_value="n")
    def test_update_event_rejected(self, mock_input, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        gc = GoogleCalendar()
        gc.service = mock_service

        event_id = "test_event_id"
        new_summary = "Updated Summary"
        new_start_date_time = "2024-08-02 3:00 PM"
        new_end_date_time = "2024-08-02 4:00 PM"

        mock_service.events.return_value.get.return_value.execute.return_value = {
            "id": event_id,
            "summary": "Old Summary",
            "start": {"dateTime": "2024-08-02T12:00:00-07:00"},
            "end": {"dateTime": "2024-08-02T14:00:00-07:00"},
        }

        result = gc.update_event(
            event_id, new_summary, new_start_date_time, new_end_date_time
        )

        self.assertEqual(result, utils.DEFAULT_USER_REJECTED_ACTION_MSG)
        self.assertFalse(mock_service.events.return_value.update.called)

    @patch("googleapiclient.discovery.build")
    def test_read_events(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        gc = GoogleCalendar()
        gc.service = mock_service

        start_date_time = "2024-08-02 12:00 AM"
        end_date_time = "2024-08-02 11:59 PM"

        mock_service.events.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": "test_event_1",
                    "summary": "Test Event 1",
                    "start": {"dateTime": "2024-08-02T10:00:00-07:00"},
                    "end": {"dateTime": "2024-08-02T11:00:00-07:00"},
                }
            ]
        }

        result = gc.read_events(start_date_time, end_date_time)

        self.assertTrue(mock_service.events.return_value.list.called)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["events"]), 1)
        event = result["events"][0]
        self.assertEqual(event["summary"], "Test Event 1")
        self.assertEqual(event["start"], "2024-08-02 10:00 AM")
        self.assertEqual(event["end"], "2024-08-02 11:00 AM")

    @patch("googleapiclient.discovery.build")
    @patch("builtins.input", return_value="Y")
    def test_delete_event_confirmed(self, mock_input, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        gc = GoogleCalendar()
        gc.service = mock_service

        event_id = "test_event_id"

        mock_service.events.return_value.get.return_value.execute.return_value = {
            "id": event_id,
            "summary": "Test Event",
            "start": {"dateTime": "2024-08-02T10:00:00-07:00"},
            "end": {"dateTime": "2024-08-02T11:00:00-07:00"},
        }

        result = gc.delete_event(event_id)

        self.assertTrue(result["success"])
        self.assertTrue(mock_service.events.return_value.delete.called)

    @patch("googleapiclient.discovery.build")
    @patch("builtins.input", return_value="n")
    def test_delete_event_rejected(self, mock_input, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        gc = GoogleCalendar()
        gc.service = mock_service

        event_id = "test_event_id"

        mock_service.events.return_value.get.return_value.execute.return_value = {
            "id": event_id,
            "summary": "Test Event",
            "start": {"dateTime": "2024-08-02T10:00:00-07:00"},
            "end": {"dateTime": "2024-08-02T11:00:00-07:00"},
        }

        result = gc.delete_event(event_id)

        self.assertEqual(result, utils.DEFAULT_USER_REJECTED_ACTION_MSG)
        self.assertFalse(mock_service.events.return_value.delete.called)


if __name__ == "__main__":
    unittest.main()
