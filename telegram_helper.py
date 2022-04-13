import logging.config
import random

import moviepy.editor as mpe
import telebot

import settings as s
from audio_helper import text_to_speech, add_background_music, create_clip

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


class Telegram:
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
        logger.info("Starting Telegram messaging")
        for lang in self.telegram_bots:
            text = self.queued["fields"][lang]
            query = self.queued["fields"][f"{lang}_q"]
            post = f"{text}\n\n___\n{self.sign}\n<i>{query}</i>"

            # if s.CREATE_AUDIO:
            #     voice_file = text_to_speech(lang, text)
            #     combined_file = add_background_music(lang, voice_file)
            if s.TELEGRAM_POST:
                self.post(lang, query, post, text)
                self.at.update_published()

    def post(self, lang, query, post, text):
        logger.info(f"Posting to telegram for {lang} language")
        chat_id = self.telegram_bots[lang]
        post_response = self.bot.send_message(chat_id, post, parse_mode='HTML')
        if s.CREATE_AUDIO:
            logger.info(f"Uploading audio file for {lang} language")
            # voice = open(combined_file, 'rb')
            if s.CREATE_VIDEO:
                logger.info(f"Creating video clip for {lang} language")
                out_clip = create_clip(lang, text)
                clip = open(out_clip, 'rb')
                tg_video = self.bot.send_video(chat_id, clip, caption=query, reply_to_message_id=post_response.message_id)
                video_url = self.bot.get_file_url(tg_video.video.file_id)
                self.at.update_video_url(video_url, lang)

            # else:
            #     self.bot.send_voice(chat_id, voice, caption=query, reply_to_message_id=post_response.message_id)


