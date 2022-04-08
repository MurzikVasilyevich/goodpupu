import json
import sys
import os
import requests
from deep_translator import GoogleTranslator
import openai
import random
import ast
from datetime import datetime
from gtts import gTTS
import telebot
import pandas as pd
import sox
import settings as s
from pyairtable import Table


def open_ai(query_in):
    openai.api_key = s.OPENAI_API_KEY
    response = openai.Completion.create(
        engine='text-davinci-002',
        prompt=query_in,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text


def main():
    os.path.exists(s.SOUND_FOLDER) or os.makedirs(s.SOUND_FOLDER)
    words = Words(s.WIKI_BASE, s.GENRE_CATEGORIES, s.PARTS_OF_SPEECH)
    words.get()
    initial_query = Query(s.QUERY_TEMPLATE, words)
    open_ai_query = OpenAIQuery(initial_query)
    open_ai_query.process_query()
    table = Table(s.AIRTABLE_KEY, s.AIRTABLE_BASE, s.AIRTABLE_TABLE)
    telegram_bots = s.TELEGRAM_BOTS
    bot_token = s.TELEGRAM_API_KEY
    bot = telebot.TeleBot(bot_token, parse_mode=None)
    broadcast(bot, open_ai_query, telegram_bots, table)
    # broadcast_confirmed(bot, open_ai_query, telegram_bots, table, get_at_confirmed(table))


def get_at_confirmed(table):
    at_queue = (table.first(formula="AND(confirmed=1,published=0,en)"))
    return at_queue['id']


def broadcast(bot, open_ai_query, telegram_bots, table):
    pure = open_ai_query.query_fixed.replace("Write a ", "").replace("\n", "")
    dtt = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    at_id = table.create({"datetime": dtt,
                          "query": open_ai_query.query_in.query, "query_fixed": open_ai_query.query_fixed})['id']
    for lang in telegram_bots:
        pure_l = GoogleTranslator(target=lang).translate(open_ai_query.query_fixed.replace("Write a ", ""))
        text_lang = open_ai_query.result if lang == 'en' else GoogleTranslator(target=lang).translate(
            open_ai_query.result)
        table.update(at_id, {lang: text_lang})
        text = f"{open_ai_query.result}\n\n___\n{s.SIGNATURE}\n{dtt}\n<i>{pure}</i>" if lang == 'en' else \
            f"{GoogleTranslator(target=lang).translate(open_ai_query.result)}\n\n___\n{s.SIGNATURE}\n{dtt}\n<i>{pure_l}</i>"
        combined_file = None
        if s.CREATE_AUDIO:
            voice_file = text_to_speech(lang, open_ai_query)
            combined_file = add_background_music(lang, voice_file)
        if s.TELEGRAM_POST:
            post_telegram(bot, combined_file, lang, pure_l, telegram_bots, text)


def add_background_music(lang, voice_file):
    music_file = get_music()
    combined_file = os.path.join(s.SOUND_FOLDER, f"{lang}_m.mp3")
    cbn = sox.Combiner()
    cbn.set_input_format(file_type=['mp3', 'mp3'])
    seconds = sox.file_info.duration(voice_file)
    rate = sox.file_info.sample_rate(voice_file)
    trn = sox.Transformer()
    trn.trim(0, seconds)
    trn.fade(fade_in_len=1, fade_out_len=2)
    music_file_trimmed = music_file.replace('.mp3', '_trimmed.mp3')
    trn.set_output_format(rate=rate)
    trn.build(music_file, music_file_trimmed)
    cbn.build([voice_file, music_file_trimmed], combined_file, 'mix', input_volumes=[1, 0.2])
    return combined_file


def text_to_speech(lang, open_ai_query):
    voice_file = os.path.join(s.SOUND_FOLDER, f"{lang}.mp3")
    voice_text = open_ai_query.result if lang == 'en' else GoogleTranslator(target=lang).translate(open_ai_query.result)
    tts_file = gTTS(text=voice_text, lang=lang, slow=False)
    tts_file.save(voice_file)
    return voice_file


def post_telegram(bot, combined_file, lang, pure_l, telegram_bots, text):
    chat_id = telegram_bots[lang]
    post_response = bot.send_message(chat_id, text, parse_mode='HTML')
    if s.CREATE_AUDIO and combined_file:
        voice = open(combined_file, 'rb')
        bot.send_voice(chat_id, voice, caption=pure_l, reply_to_message_id=post_response.message_id)


class OpenAIQuery:
    def __init__(self, query_in):
        self.query_in = query_in
        self.query_fixed = ''
        self.result = self.query_in

    def process_query(self):
        self.query_fixed = open_ai(f"Correct this to standard English:\n\n{self.query_in.query}")
        self.result = open_ai(self.query_fixed)


def get_word(url, category):
    while True:
        request_word = requests.get(url + category)
        word = request_word.url.split('/')[-1].replace('_', ' ')
        if word.find("Category:") == -1:
            return word


class Words:
    def __init__(self, wiki_base, genre_categories, parts_of_speech):
        self.parts_of_speech = parts_of_speech
        self.genre_category = random.choice(genre_categories)
        self.wiki_base = wiki_base
        self.genre = ''
        self.words = {}

    def get(self):
        self.genre = self.get_genre()
        self.get_words()
        return self

    def get_genre(self):
        return get_word(self.wiki_base.format('wikipedia'), self.genre_category)

    def get_words(self):
        for part in self.parts_of_speech:
            self.words[part] = get_word(self.wiki_base.format('wiktionary'), f"English_{part}s")


class WordsEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Words):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


class Query:
    def __init__(self, query_template, words):
        self.genre = words.genre
        self.adjective = words.words['adjective']
        self.verb = words.words['verb']
        self.noun = words.words['noun']
        self.adverb = words.words['adverb']
        self.query_template = query_template
        self.query = self.query_template.format(self.genre, self.adjective, self.verb, self.noun, self.adverb)

    def get(self):
        return self

    def get_adjective(self, ps_id):
        # 21808216
        url = f"https://petscan.wmflabs.org/?format=csv&psid={ps_id}"
        df = pd.read_csv(url)
        self.adjective = df.sample(1).iloc[0]['title'].replace("_", " ")


def get_music():
    url = "http://ccmixter.org/api/query?f=csv&dataview=links_dl&limit=30&type=instrumentals"
    df = pd.read_csv(url)
    audio_url = df.sample(1).iloc[0]['download_url']
    payload = {}
    headers = {
        'Referer': 'http://ccmixter.org/'
    }
    filename = os.path.join(s.SOUND_FOLDER, audio_url.split("/")[-1])
    r = requests.get(audio_url, payload, headers=headers)
    open(filename, 'wb').write(r.content)
    return filename


if __name__ == '__main__':
    sys.exit(main())
