import logging.config
import telebot
import settings as s
import vimeo
import urllib.parse

from audio_helper import create_clip

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


class VideoManager:
    def __init__(self, at):
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

            if s.POST_TELEGRAM:
                self.post_telegram(lang, query, post, text)
                self.at.update_published()

            if s.POST_VIMEO:
                self.post_vimeo(lang, query, text)
                self.at.update_published()

    def post_vimeo(self, lang, query, text):
        logger.info(f"Posting to vimeo for {lang} language")

        logger.info(f"Creating video clip for {lang} language")
        out_clip = create_clip(lang, text, lang in s.VIMEO_LANGUAGES)

        if lang in s.VIMEO_LANGUAGES:
            client = vimeo.VimeoClient(
                token=s.VIMEO_TOKEN,
                key=s.VIMEO_KEY,
                secret=s.VIMEO_SECRET
            )
            data = {"name": f"{query}", "description": f"{text}"}
            print(data)
            video_id = client.upload(out_clip, data=data)
            video_url = f"https://vimeo.com/{video_id.split('/')[-1]}"
            if video_id:
                self.at.update_vimeo_url(video_url)
            return video_url
        else:
            logger.info(f"{lang} language is not supported")
            return None

    def post_telegram(self, lang, query, post, text):
        logger.info(f"Posting to telegram for {lang} language")
        video_urls = []
        chat_id = self.telegram_bots[lang]
        if s.TG_POST_TEXT:
            post_response = self.bot.send_message(chat_id, post, parse_mode='HTML')
        if s.CREATE_AUDIO:
            logger.info(f"Uploading audio file for {lang} language")

            if s.CREATE_VIDEO:
                logger.info(f"Creating video clip for {lang} language")
                out_clip = create_clip(lang, text)
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
            self.at.update_video_url(video_urls, lang)

