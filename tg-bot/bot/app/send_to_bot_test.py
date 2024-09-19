import requests
from secrets import TELEGRAM_BOT_TOKEN, ADMIN_ID


if __name__ == '__main__':
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    params = {
        'chat_id': ADMIN_ID,
        'text': 'baby steps'
    }

    requests.get(url, params=params)
