import logging.config
import shutil

import telebot
import vimeo

import settings as s
from audio_helper import create_clip, download_video

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def trim_text(query, max_len):
    trimmed = (query[:max_len - 5] + '..') if len(query) > max_len else query
    return trimmed


class VideoManager:
    def __init__(self, at):
        self.video_back = download_video()
        self.at = at
        self.telegram_bots = s.TELEGRAM_BOTS
        self.sign = s.SIGNATURE
        self.key = s.TELEGRAM_API_KEY
        self.queued = self.at.queued
        self.bot = telebot.TeleBot(self.key, parse_mode=None)
        if self.queued:
            self.broadcast()
        else:
            logger.info("No messages to send")

    def broadcast(self):
        logger.info("Starting VideoManager messaging")
        for lang in self.telegram_bots:
            text = self.queued["fields"][lang]
            query = self.queued["fields"][f"{lang}_q"]
            post = f"{text}\n\n___\n{self.sign}\n<i>{query}</i>"
            logger.info(f"Creating video clip for {lang} language")
            out_clip = create_clip(lang, text, self.video_back)

            if s.POST_TELEGRAM:
                self.post_telegram(out_clip, lang, query, post)
            if s.POST_VIMEO:
                self.post_vimeo(out_clip, lang, query, text)
            if s.STORE_LOCAL:
                self.store_local(out_clip, lang)
            if s.POST_TELEGRAM or s.POST_VIMEO or s.STORE_LOCAL:
                self.at.update_status("published", True)
        logger.info("Finished VideoManager messaging")

    def store_local(self, out_clip, lang):
        logger.info(f"Storing local for {lang} language")
        shutil.copy(out_clip, f"{s.LOCAL_STORAGE}{lang}/{self.at.queued['fields']['id']}_{lang}.mp4")

    def post_vimeo(self, out_clip, lang, query, text):
        logger.info(f"Posting to vimeo for {lang} language")
        if lang in s.VIMEO_LANGUAGES:
            client = vimeo.VimeoClient(
                token=s.VIMEO_TOKEN,
                key=s.VIMEO_KEY,
                secret=s.VIMEO_SECRET
            )
            data = {
                "name": trim_text(query, s.VIMEO_TITLE_LENGTH),
                "description": trim_text(text, s.VIMEO_DESCRIPTION_LENGTH)
                    }
            print(data)
            video_id = client.upload(out_clip, data=data)
            video_url = f"https://vimeo.com/{video_id.split('/')[-1]}"
            if video_id:
                self.at.update_status(f"vimeo", video_url)
            return video_url
        else:
            logger.info(f"{lang} language is not supported")
            return None

    def post_telegram(self, out_clip, lang, query, post):
        logger.info(f"Posting to telegram for {lang} language")
        video_urls = []
        chat_id = self.telegram_bots[lang]
        if s.TG_POST_TEXT:
            post_response = self.bot.send_message(chat_id, post, parse_mode='HTML')
        if s.CREATE_AUDIO:
            logger.info(f"Uploading audio file for {lang} language")

            if s.CREATE_VIDEO:
                logger.info(f"Creating video clip for {lang} language")
                clip = open(out_clip, 'rb')
                if s.TG_POST_TEXT:
                    tg_video = self.bot.send_video(chat_id, clip,
                                                   caption=query,
                                                   reply_to_message_id=post_response.message_id)
                else:
                    tg_video = self.bot.send_video(chat_id, clip,
                                                   caption=query)
                video_url = self.bot.get_file_url(tg_video.video.file_id)
                if video_url:
                    video_urls.append({"url": video_url})

        if s.CREATE_VIDEO:
            self.at.update_status(f"{lang}_v", video_urls)

