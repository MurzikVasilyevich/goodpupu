import ast
import os


class POST:
    TELEGRAM = False
    VIMEO = False
    LOCAL = True
    AIRTABLE = True
    CREATE_AUDIO = True
    CREATE_VIDEO = True
    BATCH_SIZE = 2
    SLEEP_TIME = 5


class OPENARCHIVE:
    MAX_SIZE = 30 * 1024 * 1024
    MAX_RETRIES = 5


class TELEGRAM:
    BOTS = ast.literal_eval(os.environ['TELEGRAM_BOTS'])
    POST_TEXT = False
    SIGNATURE = 'MurzikVasilyevich'
    API_KEY = os.environ['TELEGRAM_BOT_TOKEN']


class AIRTABLE:
    KEY = os.environ["AIRTABLE_API_KEY"]
    BASE = 'appZxvQ7uCucsSdHI'
    TABLE_RECORDS = 'tbluBApx6wGOYs6YN'
    TABLE_FORMATS = 'tblDjnVhl824CiJok'
    TABLE_GENRES = 'tblF55j8dK6VtAiHo'


class OPENAI:
    API_KEY = os.environ["OPENAI_API_KEY"]


class VIMEO:
    TOKEN = os.environ["VIMEO_TOKEN"]
    KEY = os.environ["VIMEO_KEY"]
    SECRET = os.environ["VIMEO_SECRET"]
    LANGUAGES = ["uk"]
    TITLE_LENGTH = 128
    DESCRIPTION_LENGTH = 5000


class LOCAL:
    SOUND = "./sounds/"
    VIDEO = "./videos/"
    STORAGE = "./results/"


class LINGUISTIC:
    LANGUAGES = ["en", "uk", "ru"]
    PARTS_OF_SPEECH = ["ADJ", "ADV", "NOUN", "VERB"]
    LANGUAGE_CODES = {"en": "en-US", "uk": "uk-UA", "ru": "ru-RU"}


class CLIP:
    AUDIO_START = 2
    TEXT_WRAP = 50
