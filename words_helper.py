import random

import openai
import pandas as pd
import nltk
from nltk.corpus import wordnet as wn
import settings as s
nltk.download('wordnet')
nltk.download('omw-1.4')

import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def make_3sg_form(verb_phrase):
    verb = verb_phrase.split(" ")[0]
    if verb.endswith('y'):
        verb_sg_form = verb[:-1] + 'ies'
    elif verb.endswith(("o", "ch", "s", "sh", "x", "z")):
        verb_sg_form = verb + 'es'
    else:
        verb_sg_form = verb + 's'
    return verb_phrase.replace(verb, verb_sg_form)


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


def get_word(pos):
    words = random.sample(list(wn.all_lemma_names(getattr( wn, pos))), 5)
    return [i.replace("_", " ") for i in words]


class Words:
    def __init__(self):
        self.words = {}
        self.get_words()

    def get_words(self):
        logging.info("Getting random words")
        self.words["genre"] = pd.read_csv(s.GENRES_FILE).sample(1).iloc[0]['title']
        poss = s.PARTS_OF_SPEECH
        for pos in poss:
            self.words[pos] = get_word(pos)
        self.words["VERB"] = [make_3sg_form(i) for i in self.words["VERB"]]
