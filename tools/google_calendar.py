from datetime import datetime, timedelta
import os.path
import json

from .utils import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
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
                creds.refresh(Request())
            else:
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

    def list_events(
        self, start_date_time=None, end_date_time=None
    ):
        start_rfc3339 = None
        end_rfc3339 = None
        if start_date_time:
            start_rfc3339 = to_rfc3339(start_date_time)
        if end_date_time:
            end_rfc3339 = to_rfc3339(end_date_time)

        page_token = None
        events_list = []
        while True:
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
                event_entry = {}
                if "start" in event and "dateTime" in event["start"]:
                    event_entry["start"] = from_rfc3339(event["start"]["dateTime"])
                if "end" in event and "dateTime" in event["end"]:
                    event_entry["end"] = from_rfc3339(event["end"]["dateTime"])
                if "summary" in event:
                    event_entry["summary"] = event["summary"]
                events_list.append(event_entry)

            page_token = events.get("nextPageToken")
            if not page_token:
                break
        
        return {"success": True, "events": events_list}

    def create_event(self, start_date_time, end_date_time, summary):
        start_rfc3339 = to_rfc3339(start_date_time)
        end_rfc3339 = to_rfc3339(end_date_time)

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

        event = self.service.events().insert(calendarId="primary", body=event).execute()
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
                                "description": f"The start date in {DATE_STRING_FMT} format",
                            },
                            "end_date_time": {
                                "type": "string",
                                "description": f"The end date in {DATE_STRING_FMT} format",
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
                                "description": f"The start date in {DATE_STRING_FMT} format",
                            },
                            "end_date_time": {
                                "type": "string",
                                "description": f"The end date in {DATE_STRING_FMT} format",
                            },
                        },
                        "required": ["summary", "start_date_time", "end_date_time"],
                    },
                },
            },
        ]

    def process_function_calls(self, function_calls):
        results = []
        for call in function_calls:
            func_name = call.function.name
            if func_name.startswith("calendar_"):
                func_name = func_name.split("calendar_")[1]
                arguments = json.loads(call.function.arguments)
                print(arguments)

                if func_name == "read_events":
                    result = self.list_events(
                        start_date_time=arguments.get("start_date_time"),
                        end_date_time=arguments.get("end_date_time"),
                    )
                elif func_name == "create_event":
                    result = self.create_event(
                        start_date_time=arguments.get("start_date_time"),
                        end_date_time=arguments.get("end_date_time"),
                        summary=arguments["summary"],
                    )
                else:
                    result = None

                results.append({"tool_call_id": call.id, "output": str(result)})
        return results


if __name__ == "__main__":
    cal = GoogleCalendar()
    cal.authenticate()
    # cal.get_or_create_calendar()
    cal.list_events("2024-07-20 12:00 AM", "2024-07-30 12:00 PM")
    # print(to_rfc3339("2024-07-20", "12:00"))
    #cal.create_event("2024-08-02", "12:00", "2024-08-02", "14:00", "test event")
