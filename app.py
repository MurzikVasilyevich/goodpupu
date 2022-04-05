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


def open_ai(query_in):
    openai.api_key = os.environ['OPENAI_API_KEY']
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
    genre_categories = ['Style_(fiction)', 'Genres_of_poetry']
    parts_of_speech = ['noun', 'verb', 'adjective', 'adverb']
    wiki_base = os.environ['WIKI_BASE']
    query_template = os.environ['QUERY_TEMPLATE']
    words = Words(wiki_base, genre_categories, parts_of_speech)
    words.get()
    print(json.dumps(words.words, indent=4))
    initial_query = Query(query_template, words)
    print(initial_query.query)
    open_ai_query = OpenAIQuery(initial_query)
    open_ai_query.process_query()
    print(open_ai_query.query_fixed)
    print(open_ai_query.result)
    dtt = datetime.now()
    telegram_bots = ast.literal_eval(os.environ['TELEGRAM_BOTS'])

    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    bot = telebot.TeleBot(bot_token, parse_mode=None)

    for lang in telegram_bots:
        chat_id = telegram_bots[lang]
        pure = open_ai_query.query_fixed.replace("Write a ", "").replace("\n", "")
        pure_l = GoogleTranslator(target=lang).translate(open_ai_query.query_fixed.replace("Write a ", ""))
        text = f"{open_ai_query.result}\n\n___\nMurzikVasilyevich\n{dtt}\n<i>{pure}</i>" if lang == 'en' else \
            f"{GoogleTranslator(target=lang).translate(open_ai_query.result)}\n\n___\nMurzikVasilyevich\n{dtt}\n<i>{pure_l}</i>"

        chat_id = telegram_bots[lang]
        voice_mytext = open_ai_query.result if lang == 'en' else GoogleTranslator(target=lang).translate(open_ai_query.result)
        myobj = gTTS(text=voice_mytext, lang=lang, slow=False)
        myobj.save(f"{lang}.mp3")
        voice_file = f"{lang}.mp3"
        music_file = get_music()
        combined_file = f"{lang}_m.mp3"
        cbn = sox.Combiner()
        seconds = sox.file_info.duration(voice_file)
        rate = sox.file_info.sample_rate(voice_file)
        trn = sox.Transformer()
        trn.trim(0, seconds)
        trn.fade(fade_in_len=1, fade_out_len=2)
        music_file_trimmed = music_file.replace('.mp3', '_trimmed.mp3')
        trn.set_output_format(rate=rate)
        trn.build(music_file, music_file_trimmed)
        cbn.build(
            [voice_file, music_file_trimmed], combined_file, 'mix', input_volumes=[1, 0.3]
        )
        post_response = bot.send_message(chat_id, text, parse_mode='HTML')
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

    def get_adjective(self):
        url = "https://petscan.wmflabs.org/?format=csv&psid=21808216"
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
    filename = audio_url.split("/")[-1]
    r = requests.get(audio_url, payload, headers=headers)
    open(filename, 'wb').write(r.content)
    return filename


if __name__ == '__main__':
    sys.exit(main())
