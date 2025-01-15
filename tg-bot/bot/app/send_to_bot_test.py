import requests
from secrets import TELEGRAM_BOT_TOKEN, ADMIN_IDS


if __name__ == '__main__':
    for admin_id in ADMIN_IDS:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        params = {
            'chat_id': admin_id,
            'text': 'baby steps'
        }

        requests.get(url, params=params)
