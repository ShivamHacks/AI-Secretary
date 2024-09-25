from datetime import datetime
from . import utils


class TaskManager:

    def __init__(self, task_list):
        self.task_list = task_list

    def create_task(self, task, deadline, category):
        new_task = {"task": task, "deadline": deadline, "category": category}
        self.task_list.append(new_task)
        return {"success": True, "message": "Task added successfully"}

    def update_task(
        self, task_index, new_task=None, new_deadline=None, new_category=None
    ):
        if task_index < 0 or task_index >= len(self.task_list):
            return {"success": False, "error": "Task index out of range"}

        task = self.task_list[task_index]
        if new_task:
            task["task"] = new_task
        if new_deadline:
            task["deadline"] = new_deadline
        if new_category:
            task["category"] = new_category

        return {"success": True, "message": "Task updated successfully"}

    def delete_task(self, task_index):
        if task_index < 0 or task_index >= len(self.task_list):
            return {"success": False, "error": "Task index out of range"}

        del self.task_list[task_index]
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
                                "description": "The deadline of the task",
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
                            "task_index": {
                                "type": "integer",
                                "description": "The index of the task to update",
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
                        "required": ["task_index"],
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
                            "task_index": {
                                "type": "integer",
                                "description": "The index of the task to delete",
                            }
                        },
                        "required": ["task_index"],
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


# Sample usage:
if __name__ == "__main__":
    task_list = []
    task_manager = TaskManager(task_list)
    print(
        task_manager.create_task(
            "Finish project report",
            datetime(2024, 10, 10).strftime(utils.DATE_STRING_FMT),
            "Work",
        )
    )
    print("Tasks: ", task_list)
    print(task_manager.update_task(0, new_task="Complete final project report"))
    print("Tasks: ", task_list)
    print(task_manager.delete_task(0))
    print("Tasks: ", task_list)
