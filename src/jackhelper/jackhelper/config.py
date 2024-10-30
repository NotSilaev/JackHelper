import os
from dotenv import load_dotenv


load_dotenv()


DJANGO_SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

WHITE_LIST = list(map(int, os.environ.get("WHITE_LIST").split(',')))

AUTODEALER_DB_DSN_VLG = os.environ.get("AUTODEALER_DB_DSN_VLG")
AUTODEALER_DB_DSN_VLZ = os.environ.get("AUTODEALER_DB_DSN_VLZ")
TEST_AUTODEALER_DB_DSN_VLG = os.environ.get("TEST_AUTODEALER_DB_DSN_VLG")
TEST_AUTODEALER_DB_DSN_VLZ = os.environ.get("TEST_AUTODEALER_DB_DSN_VLZ")
AUTODEALER_DB_USER = os.environ.get("AUTODEALER_DB_USER")
AUTODEALER_DB_PASS = os.environ.get("AUTODEALER_DB_PASS")

TELEGRAM_LOGS_BOT_TOKEN = os.environ.get("TELEGRAM_LOGS_BOT_TOKEN")
TELEGRAM_LOGS_BOT_USERS = list(map(int, os.environ.get("TELEGRAM_LOGS_BOT_USERS").split(',')))