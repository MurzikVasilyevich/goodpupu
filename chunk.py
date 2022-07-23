from datetime import datetime
from airtable_helper import Airtable
from openai_helper import open_ai
from words_helper import Words, prepare_fmt
from translation_helper import Translations
import settings as s


class Chunk:
    def __init__(self):
        self.generated_on = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        self.at = Airtable(self)
        self.source = Source(self)
        self.texter = Texter(self)


class Source:
    def __init__(self, chunk):
        self.chunk = chunk
        self.format, self.genre = self.chunk.at.get_format()


class Texter:
    def __init__(self, chunk):
        self.languages = s.LANGUAGES
        self.chunk = chunk
        self.words = Words()
        self.query = (prepare_fmt(self.chunk.source.format["fields"]["Format"])).format(**vars(self.words)["words"])
        self.open_ai_result = open_ai(f"Write a {self.chunk.source.genre['fields']['Name']} about how" +
                                      self.query).strip()
        self.translations = Translations(self, self.languages)


class Files:
    def __init__(self):
        self.srt = ""
        self.txt = ""
        self.music = ""
        self.video = ""
        self.clip = ""
        self.clip_srt = ""
