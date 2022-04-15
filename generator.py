import os
from datetime import datetime

import pandas as pd

import settings as s
from airtable_helper import get_fmt, prepare_fmt
from translation_helper import Translations
from words_helper import Words, open_ai


class Generator:
    def __init__(self):
        self.generated_on = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        if s.CREATE_AUDIO:
            os.path.exists(s.SOUND_FOLDER) or os.makedirs(s.SOUND_FOLDER)
        if s.CREATE_VIDEO:
            os.path.exists(s.VIDEO_FOLDER) or os.makedirs(s.VIDEO_FOLDER)
        self.query_template = get_fmt()
        self.words = Words()
        self.query = (prepare_fmt(self.query_template["fields"]["Format"])).format(**vars(self.words)["words"])
        self.open_ai_result = open_ai("Write a " + self.query).strip()
        self.languages = s.LANGUAGES
        self.translations = Translations(self)
