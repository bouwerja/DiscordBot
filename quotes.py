import requests
from datetime import datetime as dt

def get_Quote():
    URL = "https://stoic.tekloon.net/stoic-quote"
    req_result = requests.get(url=URL)
    result = req_result.json()
    return {
        'Author': result['data']['author'],
        'Quote': result['data']['quote'],
        'DateRecordCreated': dt.now().strftime("%Y-%m-%d %H:%M:%S")
    }