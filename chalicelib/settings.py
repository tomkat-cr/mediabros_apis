import os
from dotenv import find_dotenv, load_dotenv


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


class settings:
    DEBUG = True if os.environ.get('APP_DEBUG', '0') == '1' else False
    APP_NAME = os.environ.get('APP_NAME')
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    SERVER_NAME = os.environ.get('SERVER_NAME')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    DB_URI = os.environ.get('DB_URI')
    DB_NAME = os.environ.get('DB_NAME')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ALGORITHM = os.environ.get('ALGORITHM', "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get(
        'ACCESS_TOKEN_EXPIRE_MINUTES', '30'
    )
    JWT_ENABLED = os.environ.get("JWT_ENABLED", "1")
    AUTH0_ENABLED = os.environ.get("AUTH0_ENABLED", "0")
