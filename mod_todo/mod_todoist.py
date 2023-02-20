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
        tasks = self.get_tasks()
        # Loop through the items and pull out the ones of interest
        for task in tasks:
            if task.checked == 0:
                if task.due:
                    items.append({
                        "content": item.content,
                        "priority": item.priority,
                        "labels": item.labels,
                        "due": item.due.date
                    })
                else:
                    items.append({
                        "content": item.content,
                        "priority": item.priority,
                        "labels": item.labels,
                        "due": 0
                    })

            # Sort the array by priority
            items = sorted(items, key=lambda i: i['priority'])
            unicode(items).encode('utf8')
            # Reverse list, since Todoist sets priority in reverse.
            # On web interface HIGH=Priority1, but stored in API as 4. who knows?!
            items.reverse()

        return items
