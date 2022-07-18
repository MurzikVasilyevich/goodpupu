import sys

from airtable_helper import Airtable
from audio_helper import get_video
from generator import Generator
from video_helper import VideoManager

import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def main():
    logging.info("Starting main")
    gen = Generator()
    logging.info("Starting Generation is done")
    at = Airtable(gen)
    logging.info("Posted to Airtable")
    get_video()
    vm = VideoManager(at)


if __name__ == '__main__':
    sys.exit(main())
