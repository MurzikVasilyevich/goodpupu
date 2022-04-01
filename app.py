import sys
import os
import requests as requests
from deep_translator import GoogleTranslator
import openai
import random


def open_ai(query_in):
    openai.api_key = os.environ['OPENAI_API_KEY']
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=query_in,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text


def get_word(url, category):
    request_word = requests.get(url+category)
    word = request_word.url.split('/')[-1].replace('_', ' ')
    return word


def telegram_post(bot_token, chat_id, text):
    requests.post(
        'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_token, chat_id, text))


def main():
    query = format_query()
    query_fixed = open_ai("Correct this to standard English:\n\n" + query)
    good_pupu_en = open_ai(query_fixed)

    good_pupu_ru = GoogleTranslator(source='en', target='ru').translate(good_pupu_en)
    good_pupu_uk = GoogleTranslator(source='en', target='uk').translate(good_pupu_en)
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']

    telegram_post(bot_token, "@goodpupu", good_pupu_ru)
    telegram_post(bot_token, "@goodpupua", good_pupu_uk)
    telegram_post(bot_token, "@goodpoopoo", good_pupu_en)


def format_query():
    wiki_base = os.environ['WIKI_BASE']
    wiktionary_base = os.environ['WIKTIONARY_BASE']
    styles = ['Style_(fiction)', 'Genres_of_poetry']
    genre_class = random.choice(styles)
    genre = get_word(wiki_base, genre_class)
    noun = get_word(wiktionary_base, 'English_nouns')
    verb = get_word(wiktionary_base, 'English_verbs')
    adjective = get_word(wiktionary_base, 'English_adjectives')
    adverb = get_word(wiktionary_base, 'English_adverbs')
    query_template = os.environ['QUERY_TEMPLATE']
    query = query_template.format(genre, adjective, verb, noun, adverb)
    return query


if __name__ == '__main__':
    sys.exit(main())
