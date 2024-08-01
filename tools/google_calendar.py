from datetime import datetime, timedelta
import os.path

from utils import *

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
        self, start_date=None, start_time=None, end_date=None, end_time=None
    ):
        start_rfc3339 = None
        end_rfc3339 = None
        if start_date and start_time:
            start_rfc3339 = to_rfc3339(start_date, start_time)
        if end_date and end_time:
            end_rfc3339 = to_rfc3339(end_date, end_time)

        page_token = None
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
                print(event["summary"])
            page_token = events.get("nextPageToken")
            if not page_token:
                break

    def create_event(self, start_date, start_time, end_date, end_time, summary):
        start_rfc3339 = to_rfc3339(start_date, start_time)
        end_rfc3339 = to_rfc3339(end_date, end_time)

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


if __name__ == "__main__":
    cal = GoogleCalendar()
    cal.authenticate()
    # cal.get_or_create_calendar()
    #cal.list_events("2024-07-20", "12:00", "2024-07-30", "12:00")
    # print(to_rfc3339("2024-07-20", "12:00"))
    cal.create_event("2024-08-02", "12:00", "2024-08-02", "14:00", "test event")
