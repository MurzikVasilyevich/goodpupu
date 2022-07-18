import ast
import os

TELEGRAM_BOTS = ast.literal_eval(os.environ['TELEGRAM_BOTS'])
TG_POST_TEXT = False
SIGNATURE = 'MurzikVasilyevich'
AIRTABLE_KEY = os.environ["AIRTABLE_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
TELEGRAM_API_KEY = os.environ['TELEGRAM_BOT_TOKEN']
AIRTABLE_BASE = 'appZxvQ7uCucsSdHI'
AIRTABLE_TABLE_RECORDS = 'tbluBApx6wGOYs6YN'
AIRTABLE_TABLE_FORMATS = 'tblDjnVhl824CiJok'
AIRTABLE_TABLE_GENRES = 'tblF55j8dK6VtAiHo'
SOUND_FOLDER = "./sounds/"
VIDEO_FOLDER = "./videos/"
VIDEO_BACK_NAME = "./videos/archive.mp4"
GENRES_FILE = "./dictionaries/genres.csv"
LANGUAGES = ["en", "uk", "ru"]
PARTS_OF_SPEECH = ["ADJ", "ADV", "NOUN", "VERB"]
AUDIO_START = 2
VIMEO_TOKEN = os.environ["VIMEO_TOKEN"]
VIMEO_KEY = os.environ["VIMEO_KEY"]
VIMEO_SECRET = os.environ["VIMEO_SECRET"]
VIMEO_LANGUAGES = ["uk"]

POST_TELEGRAM = False
POST_VIMEO = True
CREATE_AUDIO = True
CREATE_VIDEO = True
