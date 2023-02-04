# telegram_utilities.py
# Telegram error reporting
import os
import sys
import requests

from chalicelib.settings import settings
from chalicelib.utility_general import log_normal


def send_tg_message(user_id, message):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    # Send the message
    url = 'https://api.telegram.org/bot' + bot_token + \
        '/sendMessage?chat_id=' + user_id + \
        '&text=' + str(message)
    response = requests.get(url)
    log_normal(response.content)
    return response


def report_error_to_tg_group(api_response):
    if not api_response['error']:
        return
    return send_tg_message(os.environ['TELEGRAM_CHAT_ID'], {
        'type': 'ERROR in a Mediabros API',
        'app_name': settings.APP_NAME,
        'server_name': settings.SERVER_NAME,
        'calling_func': sys._getframe(1).f_code.co_name,
        'error_message': api_response['error_message'],
    })
