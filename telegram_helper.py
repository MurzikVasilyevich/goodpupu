import telebot

import settings as s
from audio_helper import text_to_speech, add_background_music
import logging.config
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
        self.broadcast()

    def broadcast(self):
        logger.info("Starting Telegram messaging")
        for lang in self.telegram_bots:
            text = self.queued["fields"][lang]
            query = self.queued["fields"][f"{lang}_q"]
            post = f"{text}\n\n___\n{self.sign}\n<i>{query}</i>"
            combined_file = None

            if s.CREATE_AUDIO:
                voice_file = text_to_speech(lang, text)
                combined_file = add_background_music(lang, voice_file)
            if s.TELEGRAM_POST:
                self.post(combined_file, lang, query, post)
                self.at.update_published()

    def post(self, combined_file, lang, query, text):
        logger.info(f"Posting to telegram for {lang} language")
        chat_id = self.telegram_bots[lang]
        post_response = self.bot.send_message(chat_id, text, parse_mode='HTML')
        if s.CREATE_AUDIO and combined_file:
            logger.info(f"Uploading audio file for {lang} language")
            voice = open(combined_file, 'rb')
            self.bot.send_voice(chat_id, voice, caption=query, reply_to_message_id=post_response.message_id)
