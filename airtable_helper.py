from pyairtable import Table

import settings as s
import logging.config
import random

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def get_format():
    formats_table = Table(s.AIRTABLE_KEY, s.AIRTABLE_BASE, s.AIRTABLE_TABLE_FORMATS)
    genres_table = Table(s.AIRTABLE_KEY, s.AIRTABLE_BASE, s.AIRTABLE_TABLE_GENRES)
    formats = formats_table.all(formula="Enabled")
    fmt = random.choice(formats)
    genres = genres_table.all(formula="Enabled")
    gnr = random.choice(genres)
    # format = fmt["fields"]["Format"]
    # fmt_prepared = prepare_fmt(fmt)
    # return f"{{genre}} about how {fmt_prepared}"
    return fmt, gnr


def prepare_fmt(fmt):
    poss = s.PARTS_OF_SPEECH
    for pos in poss:
        op = 0
        while fmt.find(f"{{{pos}}}") != -1:
            fmt = fmt.replace(f"{{{pos}}}", f"{{{pos}[{op}]}}", 1)
            op += 1
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
        translations["Format"] = [self.gen.fmt["id"]]
        translations["Genre"] = [self.gen.gnr["id"]]
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

    def update_vimeo_url(self, url):
        resp = self.records_table.update(str(self.queued["id"]), {f"vimeo": url})
        logging.info(f"Updating vimeo_url: {resp}")

    def update_speech_url(self, urls):
        resp = self.records_table.update(str(self.queued["id"]), {"speech": urls})
        logging.info(f"Updating speech_url: {resp}")
