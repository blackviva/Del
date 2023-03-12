import os

class Config(object):
    API_ID = int(os.environ.get("API_ID", ""))
    API_HASH = os.environ.get("API_HASH", "") 
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 
    AUTH_CHANNEL = int(os.environ.get("AUTH_CHANNEL", ""))
    AUTH_CHANNEL2 = int(os.environ.get("AUTH_CHANNEL2", ""))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))
    OWNER_ID = int(os.environ.get("OWNER_ID", ""))
