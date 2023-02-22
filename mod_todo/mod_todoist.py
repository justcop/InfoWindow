import requests
import logging
import json

class ToDo:
    def __init__(self, opts):
        logging.debug("Todo API: TODOIST")
        self.api = False
        if not opts['api_key']:
            logging.warning("Not loading Todo API, since no api key is configured")
        else:
            self.api_key = opts['api_key']
            self.headers = {"Authorization": "Bearer " + self.api_key}
            self.api_url = "https://api.todoist.com/rest/v2"
            self.tasks_api_url = self.api_url + "/tasks"

    def list(self):
        items = []
        params = {
            "filter": "(not completed)"
        }
        response = requests.get(
            self.tasks_api_url,
            headers=self.headers,
            params=params
        )

        if response.ok:
            for item in json.loads(response.content):
                if item['checked'] == 0:
                    if item.due:
                        items.append({
                            "content": item.content,
                            "priority": item.priority,
                            "labels":item.labels,
                            "due":item.due.date
                         })    
                    else:
                        items.append({
                            "content": item.content,
                            "priority": item.priority,
                            "labels":item.labels,
                            "due":0
                        })    
               

            # Sort the array by priority
            items = sorted(items, key=lambda i: i['priority'])

            # Reverse list, since Todoist sets priority in reverse.
            # On web interface HIGH=Priority1, but stored in API as 4. who knows?!
            items.reverse()

        else:
            logging.error("Failed to fetch tasks from Todoist API")

        return items
