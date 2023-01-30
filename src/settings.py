import os


class settings:
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
