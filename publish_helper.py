import logging.config
import shutil

import telebot
import vimeo

import settings as s
# from video_helper import download_video, create_clip

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def trim_text(query, max_len):
    trimmed = (query[:max_len - 5] + '..') if len(query) > max_len else query
    return trimmed


def store_local(out_clip, lang):
    logger.info(f"Storing local")
    shutil.move(out_clip, f"{s.LOCAL.STORAGE}{lang}/")


class PublishManager:
    def __init__(self, chunk):
        # self.video_back = download_video()
        self.chunk = chunk
        self.db = chunk.db
        self.telegram_bots = s.TELEGRAM.BOTS
        self.sign = s.TELEGRAM.SIGNATURE
        self.key = s.TELEGRAM.API_KEY
        self.queued = self.db.queued
        self.bot = telebot.TeleBot(self.key, parse_mode=None)
        if self.queued:
            self.broadcast()
        else:
            logger.info("No messages to send")

    def broadcast(self):
        logger.info("Starting PublishManager messaging")
        for lang in s.LINGUISTIC.LANGUAGES:
            text = self.chunk.texter.texts["result"][lang]
            query = self.chunk.texter.texts["query"][lang]
            post = f"{text}\n\n___\n{self.sign}\n<i>{query}</i>"
            logger.info(f"Creating video clip for {lang} language")
            out_clip = self.chunk.files.video['srt'][lang]

            if s.POST.TELEGRAM:
                self.post_telegram(out_clip, lang, query, post)
            if s.POST.VIMEO:
                self.post_vimeo(out_clip, lang, query, text)
            if s.POST.LOCAL:
                store_local(self.chunk.files.video['srt'][lang], lang)
            if s.POST.TELEGRAM or s.POST.VIMEO or s.POST.LOCAL:
                self.db.update_status("published", True)
        logger.info("Finished PublishManager messaging")

    def post_vimeo(self, out_clip, lang, query, text):
        logger.info(f"Posting to vimeo for {lang} language")
        if lang in s.VIMEO.LANGUAGES:
            client = vimeo.VimeoClient(
                token=s.VIMEO.TOKEN,
                key=s.VIMEO.KEY,
                secret=s.VIMEO.SECRET
            )
            data = {
                "name": trim_text(query, s.VIMEO.TITLE_LENGTH),
                "description": trim_text(text, s.VIMEO.DESCRIPTION_LENGTH)
                    }
            print(data)
            video_id = client.upload(out_clip, data=data)
            video_url = f"https://vimeo.com/{video_id.split('/')[-1]}"
            if video_id:
                self.db.update_status(f"vimeo", video_url)
            return video_url
        else:
            logger.info(f"{lang} language is not supported")
            return None

    def post_telegram(self, out_clip, lang, query, post):
        logger.info(f"Posting to telegram for {lang} language")
        video_urls = []
        chat_id = self.telegram_bots[lang]
        if s.TELEGRAM.POST_TEXT:
            post_response = self.bot.send_message(chat_id, post, parse_mode='HTML')
        if s.POST.CREATE_AUDIO:
            logger.info(f"Uploading audio file for {lang} language")

            if s.POST.CREATE_VIDEO:
                logger.info(f"Creating video clip for {lang} language")
                clip = open(out_clip, 'rb')
                if s.TELEGRAM.POST_TEXT:
                    tg_video = self.bot.send_video(chat_id, clip,
                                                   caption=query,
                                                   reply_to_message_id=post_response.message_id)
                else:
                    tg_video = self.bot.send_video(chat_id, clip,
                                                   caption=query)
                video_url = self.bot.get_file_url(tg_video.video.file_id)
                if video_url:
                    video_urls.append({"url": video_url})

        if s.POST.CREATE_VIDEO:
            self.db.update_status(f"{lang}_v", video_urls)
        logger.info(f"Finished posting to telegram for {lang} language")
