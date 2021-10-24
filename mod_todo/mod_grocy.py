import requests
import logging
import json
import datetime


class test:
    def __init__(self, opts):
        logging.debug("Grocy API: GROCY")
        self.api = False
        headers = {
            'accept': 'application/json',
            'GROCY-API-KEY': opts['api_key'],
        }
        if not opts['api_key']:
            logging.warning("Not loading Todo API, since no api key is configured")
        else:
            self.api = requests.get("https://"+opts['server']+":"+opts['port']+"/api/stock", headers=headers)

    def list(self):
        today = datetime.date.today()
        items = []
        # Loop through original array from Grocy and pull out items by soonest best before date
        if self.api:
            data = json.loads(self.api.content)
            for item in data:
                best_before = item['best_before_date']
                best_before_date = datetime.date(int(best_before[0:4]),int(best_before[5:7]),int(best_before[8:10]))
                days = best_before_date - today
                items.append({
                    "content": item['product']['name'],
                    "best_before": item['best_before_date'],
                    "location": item['product']['location'],
                    "days": str(days.days)
                    })

        items = sorted(items, key = lambda i: i['best_before'])


        return items
