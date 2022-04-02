import sys
import os
import requests
from deep_translator import GoogleTranslator
import openai
import random
import ast


def open_ai(query_in):
    openai.api_key = os.environ['OPENAI_API_KEY']
    response = openai.Completion.create(
        engine=os.environ['OPENAI_ENGINE'],
        prompt=query_in,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text


def telegram_post(bot_token, chat_id, text):
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={text}')


def main():
    genre_categories = ['Style_(fiction)', 'Genres_of_poetry']
    parts_of_speech = ['noun', 'verb', 'adjective', 'adverb']
    wiki_base = os.environ['WIKI_BASE']
    query_template = os.environ['QUERY_TEMPLATE']
    words = Words(wiki_base, genre_categories, parts_of_speech)
    words.get()
    initial_query = Query(query_template, words)

    open_ai_query = OpenAIQuery(initial_query)
    open_ai_query.process_query()
    print(open_ai_query)
    telegram_bots = ast.literal_eval(os.environ['TELEGRAM_BOTS'])

    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    for lang in telegram_bots:
        telegram_post(bot_token, telegram_bots[lang],
                      open_ai_query.result if lang == 'en'
                      else GoogleTranslator(target=lang).translate(open_ai_query.result))


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


if __name__ == '__main__':
    sys.exit(main())
