import datetime
import json
import uuid


class CalendarManager:
    def __init__(self, file_name="calendar.txt"):
        self.file_name = file_name
        self.events = []
        self.load_calendar()

    def load_calendar(self):
        try:
            with open(self.file_name, "r") as file:
                self.events = json.load(file)
        except FileNotFoundError:
            self.events = []

    def save_calendar(self):
        with open(self.file_name, "w") as file:
            json.dump(self.events, file, default=str)

    def read_events(self, start_date, end_date):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        return [
            event
            for event in self.events
            if start_date
            <= datetime.datetime.strptime(event["start_date"], "%Y-%m-%d")
            <= end_date
        ]

    def create_event(self, name, start_date, end_date, start_time, end_time):
        event = {
            "id": str(uuid.uuid4()),
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
            "start_time": start_time,
            "end_time": end_time,
        }
        self.events.append(event)
        self.save_calendar()
        return {"success": True, "event": event}

    def modify_event(
        self,
        event_id,
        new_name=None,
        new_start_date=None,
        new_end_date=None,
        new_start_time=None,
        new_end_time=None,
    ):
        for event in self.events:
            if event["id"] == event_id:
                if new_name:
                    event["name"] = new_name
                if new_start_date:
                    event["start_date"] = new_start_date
                if new_end_date:
                    event["end_date"] = new_end_date
                if new_start_time:
                    event["start_time"] = new_start_time
                if new_end_time:
                    event["end_time"] = new_end_time
                self.save_calendar()
                return {"success": True, "event": event}
        return {"success": False, "message": "Event not found"}

    def delete_event(self, event_id):
        for event in self.events:
            if event["id"] == event_id:
                self.events.remove(event)
                self.save_calendar()
                return {"success": True, "event_id": event_id}
        return {"success": False, "message": "Event not found"}

    def save_to_file(self):
        self.save_calendar()

    def read_from_file(self):
        self.load_calendar()

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
                            "start_date": {
                                "type": "string",
                                "description": "The start date in YYYY-MM-DD format",
                            },
                            "end_date": {
                                "type": "string",
                                "description": "The end date in YYYY-MM-DD format",
                            },
                        },
                        "required": ["start_date", "end_date"],
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
                            "name": {
                                "type": "string",
                                "description": "The name of the event",
                            },
                            "start_date": {
                                "type": "string",
                                "description": "The start date in YYYY-MM-DD format",
                            },
                            "end_date": {
                                "type": "string",
                                "description": "The end date in YYYY-MM-DD format",
                            },
                            "start_time": {
                                "type": "string",
                                "description": "The start time in HH:MM format",
                            },
                            "end_time": {
                                "type": "string",
                                "description": "The end time in HH:MM format",
                            },
                        },
                        "required": [
                            "name",
                            "start_date",
                            "end_date",
                            "start_time",
                            "end_time",
                        ],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "calendar_modify_event",
                    "description": "Modify an existing calendar event",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_id": {
                                "type": "string",
                                "description": "The unique ID of the event",
                            },
                            "new_name": {
                                "type": "string",
                                "description": "The new name of the event",
                                "default": None,
                            },
                            "new_start_date": {
                                "type": "string",
                                "description": "The new start date in YYYY-MM-DD format",
                                "default": None,
                            },
                            "new_end_date": {
                                "type": "string",
                                "description": "The new end date in YYYY-MM-DD format",
                                "default": None,
                            },
                            "new_start_time": {
                                "type": "string",
                                "description": "The new start time in HH:MM format",
                                "default": None,
                            },
                            "new_end_time": {
                                "type": "string",
                                "description": "The new end time in HH:MM format",
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
                    "description": "Delete an event from the calendar",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_id": {
                                "type": "string",
                                "description": "The unique ID of the event",
                            }
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
                func_name = func_name.split("calendar_")[1]
                arguments = json.loads(call.function.arguments)

                if func_name == "read_events":
                    result = self.read_events(
                        arguments["start_date"], arguments["end_date"]
                    )
                elif func_name == "create_event":
                    result = self.create_event(
                        arguments["name"],
                        arguments["start_date"],
                        arguments["end_date"],
                        arguments["start_time"],
                        arguments["end_time"],
                    )
                elif func_name == "modify_event":
                    result = self.modify_event(
                        arguments["event_id"],
                        arguments.get("new_name"),
                        arguments.get("new_start_date"),
                        arguments.get("new_end_date"),
                        arguments.get("new_start_time"),
                        arguments.get("new_end_time"),
                    )
                elif func_name == "delete_event":
                    result = self.delete_event(arguments["event_id"])
                else:
                    result = None

                results.append({"tool_call_id": call.id, "output": str(result)})
        return results


# Usage Example
if __name__ == "__main__":
    cal = CalendarManager()

    # Create events
    cal.create_event("Meeting", "2024-07-27", "2024-07-27", "10:00", "11:00")
    cal.create_event("Conference", "2024-08-15", "2024-08-15", "09:00", "17:00")

    # Read events in a date range
    events_in_july = cal.read_events("2024-07-01", "2024-07-31")
    print(events_in_july)

    # Modify an event
    if events_in_july:
        event_id = events_in_july[0]["id"]
        cal.modify_event(
            event_id,
            new_name="Team Meeting",
            new_start_date="2024-07-28",
            new_start_time="11:00",
            new_end_time="12:00",
        )

    # Delete an event
    event_id_to_delete = [
        event["id"] for event in cal.events if event["name"] == "Conference"
    ][0]
    cal.delete_event(event_id_to_delete)

    # Save to file
    cal.save_to_file()

    # Read from file
    cal.read_from_file()
    print(cal.events)

    # Get tool metadata
    metadata = cal.get_tool_metadata()
    print(metadata)

    # Process function calls example
    function_calls = [
        {
            "id": "call_1",
            "function": {
                "arguments": '{"start_date": "2024-07-01", "end_date": "2024-07-31"}',
                "name": "calendar_read_events",
            },
            "type": "function",
        },
        {
            "id": "call_2",
            "function": {
                "arguments": '{"name": "Workshop", "start_date": "2024-09-01", "end_date": "2024-09-01", "start_time": "14:00", "end_time": "16:00"}',
                "name": "calendar_create_event",
            },
            "type": "function",
        },
    ]

    results = cal.process_function_calls(function_calls)
    print(results)
