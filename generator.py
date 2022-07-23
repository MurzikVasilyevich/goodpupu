import os
import shutil

import settings as s
from airtable_helper import get_format
from translation_helper import Translations


class Generator:
    def __init__(self, chunk):
        self.generated_on = chunk.generated_on
        if s.CREATE_AUDIO:
            shutil.rmtree(s.SOUND_FOLDER, ignore_errors=True)
            os.path.exists(s.SOUND_FOLDER) or os.makedirs(s.SOUND_FOLDER)
        if s.CREATE_VIDEO:
            shutil.rmtree(s.VIDEO_FOLDER, ignore_errors=True)
            os.path.exists(s.VIDEO_FOLDER) or os.makedirs(s.VIDEO_FOLDER)
