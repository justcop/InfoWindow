from todoist.api import TodoistAPI
import logging


class ToDo:
    def __init__(self, opts):
        logging.debug("Todo API: TODOIST")
        self.api = False
        if not opts['api_key']:
            logging.warning("Not loading Todo API, since no api key is configured")
        else:
            self.api = TodoistAPI(opts['api_key'])
            self.api.sync()

    def list(self):
        items = []
        # Use the REST API to fetch the latest state
        state = self.api.state.get(['items'])

        # Loop through the items and pull out the ones of interest
        for item in state['items']:
            if item['checked'] == 0:
                if item['due']:
                    items.append({
                        "content": item.content,
                        "priority": item.priority,
                        "labels": item.labels,
                        "due": item.due['date']
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
