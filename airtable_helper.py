import random

from pyairtable import Table

import settings as s
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def get_fmt():
    genres_table = Table(s.AIRTABLE_KEY, s.AIRTABLE_BASE, s.AIRTABLE_TABLE_GENRES)
    genres = genres_table.all(formula="Enabled")
    fmt = random.choice(genres)["fields"]["Format"]
    return fmt


class Airtable:
    def __init__(self, gen):
        self.gen = gen
        self.records_table = Table(s.AIRTABLE_KEY, s.AIRTABLE_BASE, s.AIRTABLE_TABLE_RECORDS)
        self.id = self.post()
        self.queued = self.get_confirmed()

    def post(self):
        logging.info("Posting to Airtable")
        translations = dict(self.gen.translations.texts)
        translations["datetime"] = self.gen.generated_on
        return self.records_table.create(translations)['id']

    def get_confirmed(self):
        queued = self.records_table.first(formula="AND(confirmed=1,published=0,en)")
        if not queued:
            logging.info("!!!No queued records!!!")
        return queued

    def update_published(self):
        resp = self.records_table.update(str(self.queued["id"]), {"published": True})
        logging.info(f"Updating published: {resp}")

    def update_video_url(self, urls, lang):
        resp = self.records_table.update(str(self.queued["id"]), {f"{lang}_v": urls})
        logging.info(f"Updating video_url: {resp}")

    def update_speech_url(self, urls):
        resp = self.records_table.update(str(self.queued["id"]), {"speech": urls})
        logging.info(f"Updating video_url: {resp}")
