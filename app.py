import sys
import time

from airtable_helper import Airtable
from publish_helper import VideoManager
import settings as s

from chunk import Chunk

import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def main():
    logging.info("Starting main")

    for i in range(1, s.BATCH_SIZE):
        logging.info(f"Starting batch {i}")
        chunk = Chunk()
        chunk
        logging.info("Starting Generation is done")
        # at = Airtable(texter)
        # logging.info("Posted to Airtable")
        # if s.CREATE_AUDIO:
        #     VideoManager(at)
        # logging.info(f"Finished batch {i}")
        # logging.info(f"Sleeping for {s.SLEEP_TIME} seconds")
        # time.sleep(s.SLEEP_TIME)

    logging.info("Finished main")
    sys.exit(0)


if __name__ == '__main__':
    sys.exit(main())
