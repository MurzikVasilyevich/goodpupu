import os
import shutil

import settings as s
from airtable_helper import get_format
from translation_helper import Translations


class Generator:
    def __init__(self, chunk):
        self.generated_on = chunk.generated_on
        if s.CREATE_AUDIO:
            shutil.rmtree(s.LOCAL.SOUND, ignore_errors=True)
            os.path.exists(s.LOCAL.SOUND) or os.makedirs(s.LOCAL.SOUND)
        if s.CREATE_VIDEO:
            shutil.rmtree(s.LOCAL.VIDEO, ignore_errors=True)
            os.path.exists(s.LOCAL.VIDEO) or os.makedirs(s.LOCAL.VIDEO)
