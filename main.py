import time
import requests
from datetime import datetime

MAIN_PAGE = 'https://binh.webhook2603.click/'
API_KEY_TELE = '6562519071:AAHXRfM8nyQa_SRgaqubdaHpdUxlzIOenag'

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
