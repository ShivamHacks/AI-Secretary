import uuid
from datetime import datetime, timedelta
import os
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError

from tools import utils


class CachedGoogleCalendar:

    def __init__(self):
        self.cache = []  # Local cache of events
        self.pending_operations = []  # Accumulated CRUD operations

    def authenticate_locally(
        self,
        api_creds_path=os.path.join(os.path.dirname(__file__), "google_creds.json"),
        token_path=os.path.join(
            os.path.dirname(__file__), "google_calendar_token.json"
        ),
        scopes=["https://www.googleapis.com/auth/calendar"],
    ):
        """
        The client usually gets the access token after the user logs in and sends
        it to the server but for testing purposes, we can authenticate the client
        directly from the server.
        """
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

    def read_events_to_cache(self, start_date_time=None, end_date_time=None):
        """
        Reads all events from the Google Calendar and stores them in the local cache.
        """
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

        self.cache = events_list  # Update local cache
        return {"success": True, "events": events_list}
    
    def read_events(self, start_date_time=None, end_date_time=None):
        """
        Returns events from cache that are within the start and end date if the parameter is set.
        """
        filtered_events = []
        for event in self.cache:
            event_start = utils.from_rfc3339(event["start"]["dateTime"])
            event_end = utils.from_rfc3339(event["end"]["dateTime"])
            
            if start_date_time and event_start < start_date_time:
                continue
            if end_date_time and event_end > end_date_time:
                continue
            
            filtered_events.append(event)

        return {"success": True, "events": filtered_events}

    def create_event(self, start_date_time, end_date_time, summary):
        """
        Adds a new event to the cache and marks it for creation in Google Calendar.
        A temporary UUID is generated to act as the event ID until synced.
        """
        start_rfc3339 = utils.to_rfc3339(start_date_time)
        end_rfc3339 = utils.to_rfc3339(end_date_time)

        event = {
            "id": str(uuid.uuid4()),  # Temporary ID
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

        self.cache.append(event)
        self.pending_operations.append(("create", event))
        print(f"Event added to cache with temporary ID {event} and pending creation.")
        return {"success": True, "event": event}

    def update_event(
        self,
        event_id,
        new_summary=None,
        new_start_date_time=None,
        new_end_date_time=None,
    ):
        """
        Updates an event in the cache and marks it for updating in Google Calendar.
        """
        for event in self.cache:
            if event["id"] == event_id:
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

                # Add to pending operations
                self.pending_operations.append(("update", event_id, event))
                print(f"Event with id {event_id} updated in cache and pending update.")
                return {"success": True, "event": event}
            
        return {"success": False, "reason": f"Could not find event with id {event_id}"}

    def delete_event(self, event_id):
        """
        Deletes an event from the cache and marks it for deletion in Google Calendar.
        """
        self.cache = [event for event in self.cache if event["id"] != event_id]

        # Add to pending operations
        self.pending_operations.append(("delete", event_id))
        print(f"Event with id {event_id} deleted from cache and pending deletion.")
        return {"success": True}

    def sync_with_google_calendar(self):
        """
        Applies the pending operations (CRUD) to the actual Google Calendar.
        Updates the local cache with actual Google Calendar event IDs for new events.
        """
        for operation in self.pending_operations:
            if operation[0] == "create":
                event_data = operation[1]
                # Remove the temporary ID before sending to Google Calendar
                event_data_without_id = event_data.copy()
                event_data_without_id.pop("id", None)

                created_event = (
                    self.service.events()
                    .insert(calendarId="primary", body=event_data_without_id)
                    .execute()
                )
                print(f"Added event to google calendar: {created_event}")

                # Update the cache with the real Google Calendar event ID
                for event in self.cache:
                    if event["id"] == event_data["id"]:  # Match the temp ID
                        event["id"] = created_event["id"]  # Replace with real ID
                        break

            elif operation[0] == "update":
                event_id, updated_data = operation[1], operation[2]
                self.service.events().update(
                    calendarId="primary", eventId=event_id, body=updated_data
                ).execute()
                print(f"Updated event with id: {event_id}")
            elif operation[0] == "delete":
                event_id = operation[1]
                self.service.events().delete(
                    calendarId="primary", eventId=event_id
                ).execute()
                print(f"Deleted event with id: {event_id}")

        # Clear the pending operations list after sync
        self.pending_operations.clear()
        print(f"All pending operations synced with Google Calendar.")

    def list_cached_events(self):
        """
        Lists all events currently in the local cache.
        """
        return self.cache

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

    # NOT USED??
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
