import time
import requests
from datetime import datetime

MAIN_PAGE = 'https://binh.webhook2603.click/'
API_KEY_TELE = '6503348684:AAFlrWn8tV2OXNVc84F6NywAnh6k7lrhdUc'

def send_message():
    data = {"chat_id": "5727411972",
            "text": f'The page is dead now.\nThe time check: {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}'
            }
    requests.post(f"https://api.telegram.org/bot{API_KEY_TELE}/sendMessage", json=data)

while True:
    if requests.get(MAIN_PAGE).status_code != 200:
        send_message()
        while requests.get(MAIN_PAGE).status_code != 200:
            time.sleep(30)
    time.sleep(30)