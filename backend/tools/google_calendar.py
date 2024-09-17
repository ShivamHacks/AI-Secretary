from datetime import datetime, timedelta
import os.path
import json

from . import utils

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError


class GoogleCalendar:

    def authenticate(
        self,
        api_creds_path="google_creds.json",
        token_path="google_calendar_token.json",
        scopes=["https://www.googleapis.com/auth/calendar"],
    ):
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    print("Refresh token is invalid, deleting token file and retrying.")
                    os.remove(token_path)
                    creds = None
            if not creds:
                flow = InstalledAppFlow.from_client_secrets_file(api_creds_path, scopes)
                creds = flow.run_local_server(port=0)
                with open(token_path, "w") as token:
                    token.write(creds.to_json())

        try:
            self.service = build("calendar", "v3", credentials=creds)
        except HttpError as error:
            print(f"An error occurred: {error}")

    def get_or_create_calendar(
        self, calendar_id_path="google_calendar_id.txt", summary="TestCalendar"
    ):
        calendar = None
        if os.path.exists(calendar_id_path):
            with open(calendar_id_path, "r") as calendar_id:
                try:
                    calendar = (
                        self.service.calendars()
                        .get(calendarId=calendar_id.read())
                        .execute()
                    )
                except HttpError as error:
                    print(
                        f"An error occurred trying to get or create calendar: {error}"
                    )

        if not calendar:
            calendar = {"summary": summary, "timeZone": "America/Los_Angeles"}
            calendar = self.service.calendars().insert(body=calendar).execute()
            with open(calendar_id_path, "w") as calendar_id:
                calendar_id.write(calendar["id"])

        self.test_calendar = calendar
        self.primary_calendar = (
            self.service.calendars().get(calendarId="primary").execute()
        )

    def read_events(self, start_date_time=None, end_date_time=None):
        start_rfc3339 = None
        end_rfc3339 = None
        if start_date_time:
            start_rfc3339 = utils.to_rfc3339(start_date_time)
        if end_date_time:
            end_rfc3339 = utils.to_rfc3339(end_date_time)

        page_token = None
        events_list = []
        while True:
            try:
                events = (
                    self.service.events()
                    .list(
                        calendarId="primary",
                        timeMin=start_rfc3339,
                        timeMax=end_rfc3339,
                        pageToken=page_token,
                    )
                    .execute()
                )
                for event in events["items"]:
                    event_entry = {"id": event["id"]}
                    if "start" in event and "dateTime" in event["start"]:
                        event_entry["start"] = utils.from_rfc3339(
                            event["start"]["dateTime"]
                        )
                    if "end" in event and "dateTime" in event["end"]:
                        event_entry["end"] = utils.from_rfc3339(
                            event["end"]["dateTime"]
                        )
                    if "summary" in event:
                        event_entry["summary"] = event["summary"]
                    events_list.append(event_entry)

                page_token = events.get("nextPageToken")
                if not page_token:
                    break

            except HttpError as error:
                return {"success": False, "error": error}

        return {"success": True, "events": events_list}

    def create_event(self, start_date_time, end_date_time, summary):
        start_rfc3339 = utils.to_rfc3339(start_date_time)
        end_rfc3339 = utils.to_rfc3339(end_date_time)

        event = {
            "summary": summary,
            "start": {
                "dateTime": start_rfc3339,
                "timeZone": "America/Los_Angeles",
            },
            "end": {
                "dateTime": end_rfc3339,
                "timeZone": "America/Los_Angeles",
            },
        }

        prompt = (
            f"Create event? {summary} from {start_date_time} to {end_date_time} [Y/n]: "
        )
        if input(prompt) not in ["Y", ""]:
            return utils.DEFAULT_USER_REJECTED_ACTION_MSG

        try:
            event = (
                self.service.events().insert(calendarId="primary", body=event).execute()
            )
        except HttpError as error:
            return {"success": False, "error": error}

        return {"success": True}

    def update_event(
        self,
        event_id,
        new_summary=None,
        new_start_date_time=None,
        new_end_date_time=None,
    ):
        event = (
            self.service.events().get(calendarId="primary", eventId=event_id).execute()
        )

        old_summary = event["summary"]
        if new_summary:
            event["summary"] = new_summary
        if new_start_date_time:
            event["start"] = {
                "dateTime": utils.to_rfc3339(new_start_date_time),
                "timeZone": "America/Los_Angeles",
            }
        if new_end_date_time:
            event["end"] = {
                "dateTime": utils.to_rfc3339(new_end_date_time),
                "timeZone": "America/Los_Angeles",
            }

        prompt = (
            f"Update event?"
            f"{' New Summary: ' + new_summary if new_summary else ' Summary: ' + old_summary}"
            f"{' New Start Time: ' + new_start_date_time if new_start_date_time else ''}"
            f"{' New End Time: ' + new_end_date_time if new_end_date_time else ''}"
            " [Y/n]: "
        )

        if input(prompt) not in ["Y", ""]:
            return utils.DEFAULT_USER_REJECTED_ACTION_MSG

        try:
            updated_event = (
                self.service.events()
                .update(calendarId="primary", eventId=event["id"], body=event)
                .execute()
            )
        except HttpError as error:
            return {"success": False, "error": error}

        return {"success": True}

    def delete_event(self, event_id):
        event = (
            self.service.events().get(calendarId="primary", eventId=event_id).execute()
        )
        prompt = (
            f"Delete event? Summary: {event.get('summary', 'No Summary')}"
            f" Start: {utils.from_rfc3339(event['start']['dateTime'])}"
            f" End: {utils.from_rfc3339(event['end']['dateTime'])}"
            f" [Y/n]: "
        )
        if input(prompt) not in ["Y", ""]:
            return utils.DEFAULT_USER_REJECTED_ACTION_MSG

        self.service.events().delete(calendarId="primary", eventId=event_id).execute()
        return {"success": True}

    def get_tool_metadata(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "calendar_read_events",
                    "description": "Read events within a date range",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date_time": {
                                "type": "string",
                                "description": utils.START_DATE_PARAM_DESC,
                                "default": None,
                            },
                            "end_date_time": {
                                "type": "string",
                                "description": utils.END_DATE_PARAM_DESC,
                                "default": None,
                            },
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "calendar_create_event",
                    "description": "Create a new calendar event",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "The name or summary of the event",
                            },
                            "start_date_time": {
                                "type": "string",
                                "description": utils.START_DATE_PARAM_DESC,
                            },
                            "end_date_time": {
                                "type": "string",
                                "description": utils.END_DATE_PARAM_DESC,
                            },
                        },
                        "required": ["summary", "start_date_time", "end_date_time"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "calendar_update_event",
                    "description": "Update an existing calendar event",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_id": {
                                "type": "string",
                                "description": "The unique ID of the event",
                            },
                            "new_summary": {
                                "type": "string",
                                "description": "The new summary of the event",
                                "default": None,
                            },
                            "new_start_date_time": {
                                "type": "string",
                                "description": utils.START_DATE_PARAM_DESC,
                                "default": None,
                            },
                            "new_end_date_time": {
                                "type": "string",
                                "description": utils.END_DATE_PARAM_DESC,
                                "default": None,
                            },
                        },
                        "required": ["event_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "calendar_delete_event",
                    "description": "Delete an existing calendar event",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_id": {
                                "type": "string",
                                "description": "The unique ID of the event to delete",
                            },
                        },
                        "required": ["event_id"],
                    },
                },
            },
        ]

    def process_function_calls(self, function_calls):
        results = []
        for call in function_calls:
            func_name = call.function.name
            if func_name.startswith("calendar_"):
                method_name = func_name.split("calendar_")[1]
                method = getattr(self, method_name, None)
                if method:
                    arguments = json.loads(call.function.arguments)
                    result = method(**arguments)
                    results.append({"tool_call_id": call.id, "output": str(result)})
                else:
                    results.append(
                        {"tool_call_id": call.id, "output": "Function not found"}
                    )
        return results
    
    def process_function_call(self, function_name, args):
        method_name = function_name.split("calendar_")[1]
        method = getattr(self, method_name, None)
        if method:
            result = method(**args)
            return result

        return {"status": "error", "message": "Function not found"}


if __name__ == "__main__":
    cal = GoogleCalendar()
    cal.authenticate()
    # cal.list_events("2024-07-20 12:00 AM", "2024-07-30 12:00 PM")
    # event = cal.create_event("2024-08-02", "12:00", "2024-08-02", "14:00", "test event")
    # updated_event = cal.update_event(event.id, new_summary="updated summary")
    events = cal.read_events()["events"]
    with open("events.json", "w") as f:
        json.dump(events, f, indent=4)
