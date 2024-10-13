from datetime import datetime
from . import utils
import uuid
from database.cached_cloud_db import DataManager


class TaskManager:

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager  # updates the local cache of this

    def create_task(self, task, deadline, category):
        new_task = {
            "id": str(uuid.uuid4()),
            "task": task,
            "deadline": deadline,
            "category": category,
        }
        self.data_manager._append_to_local("todo", new_task)
        return {"success": True, "task": new_task}

    def update_task(self, task_id, new_task=None, new_deadline=None, new_category=None):
        for task in self.data_manager.get_cache("todo"):
            if task["id"] != task_id:
                continue
            if new_task:
                task["task"] = new_task
            if new_deadline:
                task["deadline"] = new_deadline
            if new_category:
                task["category"] = new_category

        return {"success": True, "message": "Task updated successfully"}

    def delete_task(self, task_id):
        for task in self.data_manager.get_cache("todo"):
            if task["id"] != task_id:
                continue
            self.data_manager._update_local(
                "todo",
                [
                    task
                    for task in self.data_manager.get_cache("todo")
                    if task["id"] != task_id
                ],
            )
        return {"success": True, "message": "Task deleted successfully"}

    def get_tool_metadata(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "task_create_task",
                    "description": "Create a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "The task description",
                            },
                            "deadline": {
                                "type": "string",
                                "description": utils.DEADLINE_PARAM_DESC,
                            },
                            "category": {
                                "type": "string",
                                "description": "The category of the task",
                            },
                        },
                        "required": ["task", "deadline", "category"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "task_update_task",
                    "description": "Update an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task to update",
                            },
                            "new_task": {
                                "type": "string",
                                "description": "The new task description",
                                "default": None,
                            },
                            "new_deadline": {
                                "type": "string",
                                "description": "The new deadline",
                                "default": None,
                            },
                            "new_category": {
                                "type": "string",
                                "description": "The new category",
                                "default": None,
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "task_delete_task",
                    "description": "Delete an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task to update",
                            }
                        },
                        "required": ["task_id"],
                    },
                },
            },
        ]

    def process_function_call(self, function_name, args):
        method_name = function_name.split("task_")[1]
        method = getattr(self, method_name, None)
        if method:
            result = method(**args)
            return result

        return {"status": "error", "message": "Function not found"}
