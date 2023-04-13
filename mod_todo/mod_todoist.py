from todoist_api_python.api import TodoistAPI
import logging

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
        # Use the REST API to fetch the latest state
        tasks = self.api.get_tasks()
        # Loop through the items and pull out the ones of interest
        for task in tasks:
                items.append({
                    "content": task.content,
                    "priority": task.priority,
                    "labels": task.labels,
                    "due": task.due.date if task.due else 0
                    })

        # Sort the array by priority
        items = sorted(items, key=lambda i: i['priority'])
        unicode(items).encode('utf8')
        # Reverse list, since Todoist sets priority in reverse.
        # On web interface HIGH=Priority1, but stored in API as 4. who knows?!
        items.reverse()

        return items
