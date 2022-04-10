import sys

from airtable_helper import Airtable
from generator import Generator
from telegram_helper import Telegram

import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def main():
    logging.info("Starting main")
    gen = Generator()
    logging.info("Starting Generation is done")
    at = Airtable(gen)
    logging.info("Posted to Airtable")
    tg = Telegram(at)


if __name__ == '__main__':
    sys.exit(main())
