from todoist_api_python.api import TodoistAPI
import logging
from datetime import date


class ToDo:
    def __init__(self, opts):
        logging.debug("Todo API: TODOIST")
        self.api = False
        if not opts['api_key']:
            logging.warning("Not loading Todo API, since no api key is configured")
        else:
            self.api = TodoistAPI(opts['api_key'])

    def list(self):
        items = []

        # Get the projects
        try:
            projects = self.api.get_projects()
            projects_dict = {project.id: project.name for project in projects}
        except Exception as error:
            logging.error(f"Error fetching projects: {error}")
            return []

        # Get the active tasks
        try:
            tasks = self.api.get_tasks()
        except Exception as error:
            logging.error(f"Error fetching tasks: {error}")
            return []

        # Loop through tasks and build items list
        for task in tasks:
          if not task.is_completed:
            project_name = projects_dict.get(task.project_id, 'Unknown')
            due_date = task.due.date if task.due else date.today().isoformat()
            item = {
                    "content": task.content,
                    "priority": task.priority,
                    "labels": task.labels,
                    "due": due_date,
                    "project_name": project_name
            }
            items.append(item)
            
        # Sort the array by priority
        items = sorted(items, key=lambda i: i['priority'])

        # Reverse list, since Todoist sets priority in reverse.
        items.reverse()

        return items
