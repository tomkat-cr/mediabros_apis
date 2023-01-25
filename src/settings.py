import os


class settings:
    APP_NAME = os.environ.get('APP_NAME')
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    SERVER_NAME = os.environ.get('SERVER_NAME')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
