import requests
import logging
import json
import datetime


class test:
    def __init__(self, opts):
        logging.debug("Grocy API: GROCY")
        self.api = False
        if not opts['api_key']:
            logging.warning("Not loading Todo API, since no api key is configured")
        else:
            try:
                self.api = requests.get("https://"+opts['server']+":"+opts['port']+"/api/stock?GROCY-API-KEY="+opts['api_key'],timeout=10)
                logging.debug(self.api.content)
            except:
                logging.debug("Unable to connect to grocy server")

            
    def list(self):
        today = datetime.date.today()
        items = []
        # Loop through original array from Grocy and pull out items by soonest best before date
        if self.api:
            grocy_connect = True
            data = json.loads(self.api.content)
            for item in data:
                logging.debug(item['product']['name'])
                best_before = item['best_before_date']
                best_before_date = datetime.date(int(best_before[0:4]),int(best_before[5:7]),int(best_before[8:10]))
                days = best_before_date - today
                items.append({
                    "content": item['product']['name'],
                    "best_before": item['best_before_date'],
                    "location": item['product']['location_id'],
                    "days": str(days.days)
                    })
        if items:
            items = sorted(items, key = lambda i: i['best_before'])
        else:
            grocy_connect = false
        return items
