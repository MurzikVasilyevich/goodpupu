from pyairtable import Table

import settings as s
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


class Airtable:
    def __init__(self, gen):
        self.gen = gen
        self.table = Table(s.AIRTABLE_KEY, s.AIRTABLE_BASE, s.AIRTABLE_TABLE)
        self.id = self.post()
        self.queued = self.get_confirmed()

    def post(self):
        logging.info("Posting to Airtable")
        translations = dict(self.gen.translations.texts)
        translations["datetime"] = self.gen.generated_on
        return self.table.create(translations)['id']

    def get_confirmed(self):
        queued = self.table.first(formula="AND(confirmed=1,published=0,en)")
        return queued

    def update_published(self):
        self.table.update(self.queued["fields"]["id"], {"published": True})
