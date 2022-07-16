import os
from datetime import datetime
import random

import pandas as pd

import settings as s
from airtable_helper import get_format, prepare_fmt
from translation_helper import Translations
from words_helper import Words, open_ai
import shutil


class Generator:
    def __init__(self):
        self.generated_on = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        if s.CREATE_AUDIO:
            shutil.rmtree(s.SOUND_FOLDER, ignore_errors=True)
            os.path.exists(s.SOUND_FOLDER) or os.makedirs(s.SOUND_FOLDER)
        if s.CREATE_VIDEO:
            shutil.rmtree(s.VIDEO_FOLDER, ignore_errors=True)
            os.path.exists(s.VIDEO_FOLDER) or os.makedirs(s.VIDEO_FOLDER)
        self.fmt, self.gnr = get_format()
        self.words = Words()
        self.query = (prepare_fmt(self.fmt["fields"]["Format"])).format(**vars(self.words)["words"])
        self.open_ai_result = open_ai(f"Write a {self.gnr['fields']['Name']} about how" + self.query).strip()
        self.languages = s.LANGUAGES
        self.translations = Translations(self)
