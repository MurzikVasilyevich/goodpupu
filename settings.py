import ast
import os

GENRE_CATEGORIES = ['Style_(fiction)', 'Genres_of_poetry', 'Literary_genres']
PARTS_OF_SPEECH = ['noun', 'verb', 'adjective', 'adverb']
WIKI_BASE = os.environ['WIKI_BASE']
QUERY_TEMPLATE = os.environ['QUERY_TEMPLATE']
TELEGRAM_BOTS = ast.literal_eval(os.environ['TELEGRAM_BOTS'])
SIGNATURE = 'MurzikVasilyevich'
AIRTABLE_KEY = os.environ["AIRTABLE_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
TELEGRAM_API_KEY = os.environ['TELEGRAM_BOT_TOKEN']
AIRTABLE_BASE = 'appZxvQ7uCucsSdHI'
AIRTABLE_TABLE = 'tblNwO619uidVQKYL'
SOUND_FOLDER = "./sounds/"

TELEGRAM_POST = False
CREATE_AUDIO = False
