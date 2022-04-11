import ast
import os

TELEGRAM_BOTS = ast.literal_eval(os.environ['TELEGRAM_BOTS'])
SIGNATURE = 'MurzikVasilyevich'
AIRTABLE_KEY = os.environ["AIRTABLE_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
TELEGRAM_API_KEY = os.environ['TELEGRAM_BOT_TOKEN']
AIRTABLE_BASE = 'appZxvQ7uCucsSdHI'
AIRTABLE_TABLE = 'tbluBApx6wGOYs6YN'
SOUND_FOLDER = "./sounds/"
VIDEO_FOLDER = "./videos/"
GENRES_FILE = "./dictionaries/genres.csv"
LANGUAGES = ["en", "uk", "ru", "ja"]

TELEGRAM_POST = True
CREATE_AUDIO = True
CREATE_VIDEO = True
