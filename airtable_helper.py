from pyairtable import Table

import settings as s
import logging.config
import random

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


class Airtable:
    def __init__(self, texter):
        self.key = s.AIRTABLE_KEY
        self.base = s.AIRTABLE_BASE
        self.tables = {
            "records": self.set_table(s.AIRTABLE_TABLE_RECORDS),
            "formats": self.set_table(s.AIRTABLE_TABLE_FORMATS),
            "genres": self.set_table(s.AIRTABLE_TABLE_GENRES)
        }
        self.id = self.post()
        # self.queued = self.get_confirmed()

    def set_table(self, table):
        return Table(self.key, self.base, table)

    def get_format(self):
        formats = self.tables["formats"].all(formula="Enabled")
        fmt = random.choice(formats)
        genres = self.tables["genres"].all(formula="Enabled")
        gnr = random.choice(genres)
        return fmt, gnr

    def post(self):
        logging.info("Posting to Airtable")
        translations = dict(self.texter.translations.texts)
        translations["Format"] = [self.texter.format["id"]]
        translations["Genre"] = [self.texter.genre["id"]]
        translations["datetime"] = self.texter.generated_on
        return self.tables["records"].create(translations)['id']

    def get_confirmed(self):
        queued = self.tables["records"].first(formula="AND(confirmed=1,published=0,en)")
        if not queued:
            logging.info("!!!No queued records!!!")
        return queued

    def update_status(self, field, value):
        resp = self.tables["records"].update(str(self.queued["id"]), {field: value})
        logging.info(f"Updating {field}: {resp}")
