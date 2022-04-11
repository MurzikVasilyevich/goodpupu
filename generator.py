import os
from datetime import datetime

import pandas as pd

import settings as s
from translation_helper import Translations
from words_helper import Words, open_ai


class Generator:
    def __init__(self):
        self.generated_on = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        if s.CREATE_AUDIO:
            os.path.exists(s.SOUND_FOLDER) or os.makedirs(s.SOUND_FOLDER)
        self.query_template = pd.read_csv("./dictionaries/formats.csv").sample(1).iloc[0]['title']
        self.words = Words()
        self.query = self.query_template.format(**vars(self.words)["words"])
        self.open_ai_result = open_ai("Write a " + self.query).strip()
        self.languages = s.LANGUAGES
        self.translations = Translations(self)