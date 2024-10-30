from .telegram_api.api_requests import send_telegram_api_request
from .config import TELEGRAM_LOGS_BOT_USERS

import os
import datetime
import logging
from textwrap import dedent


# Create a custom formatter with your desired time format
time_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] - %(message)s', datefmt=time_format)

# Create a logger and set the custom formatter
logger = logging.getLogger('custom_logger')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def addLog(level: str, text: str, send_telegram_message: bool=False) -> None:
    '''Adds new log to file, console and telegram chat.

    :param level: log level (`info`, 'debug', 'warning', 'error', 'critical').
    :param text: log text.
    :param send_telegram_message: determines whether a log will be sent to telegram chat.
    '''
    
    now = datetime.datetime.now()
    path = f"logs/{now.year}/{now.month}/{now.day}/"
    filename = path + f"log-{now.hour}.log"

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(filename, 'a') as file:
        separator_string = f"\n\n{'='*50}\n\n"
        try:
            file.write(f"{now} [{level}] - {text}" + separator_string)
        except:
            file.write(f"{now} [{level}] - {text.encode('utf-8')}" + separator_string)

    if send_telegram_message:
        disable_notification = True
        if level.lower() in ['warning', 'error', 'critical']:
            disable_notification = False

        for user_id in TELEGRAM_LOGS_BOT_USERS:
            response = send_telegram_api_request(
                request_method='POST',
                api_method='sendMessage',
                parameters={
                    'chat_id': user_id,
                    'text': dedent(
                        f'''
                        *[{level.upper()}]* _({now})_

                        `{text}`
                        '''),
                    'parse_mode': 'Markdown',
                    'disable_notification': disable_notification,
                }
            )
            
            if response['code'] == 400:
                addLog(
                    level='warning', 
                    text=dedent(f'''
                        Telegram message with last error log didn't send. 
                        API response: {response['text']}
                    ''')
                )