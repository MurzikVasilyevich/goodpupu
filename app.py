import sys
import time

from airtable_helper import Airtable
from audio_helper import get_video
from generator import Generator
from video_helper import VideoManager
import settings as s

import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def main():
    logging.info("Starting main")

    for i in range(1, s.BATCH_SIZE):
        logging.info(f"Starting batch {i}")
        gen = Generator()
        logging.info("Starting Generation is done")
        at = Airtable(gen)
        logging.info("Posted to Airtable")
        if s.CREATE_AUDIO:
            VideoManager(at)
        logging.info(f"Finished batch {i}")
        logging.info("Sleeping for 5 seconds")
        time.sleep(5)

    logging.info("Finished main")
    sys.exit(0)


if __name__ == '__main__':
    sys.exit(main())
