from jackhelper.config import (
    TELEGRAM_LOGS_BOT_TOKEN,
)

import requests

def send_telegram_api_request(request_method: str, api_method: str, parameters:dict={}, bot: str='logs') -> str:
    '''Sends request to Telegram API.

    :param request_method: http request method (`get` or `post`).
    :param api_method: the required method in Telegram API.
    :param parameters: dict of parameters which will used in the Telegram API method.
    :param bot: the bot whose token will be used to send the request.
    '''

    match bot:
        case 'logs': BOT_TOKEN = TELEGRAM_LOGS_BOT_TOKEN
        case _: return ValueError('Unavailable telegram bot token')

    request = f'''
        https://api.telegram.org/bot{BOT_TOKEN}/{api_method}?{'&'.join([f'{k}={v}' for k, v in parameters.items()])}
    '''

    if request_method == 'GET':
        r = requests.get(request)
    elif request_method == 'POST':
        r = requests.post(request)

    response = {
        'code': r.status_code,
        'text': r.text,
    }
    
    return response