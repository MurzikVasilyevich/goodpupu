import logging.config
import random
import nltk
from nltk.corpus import wordnet as wn
import settings as s

nltk.download('wordnet')
nltk.download('omw-1.4')
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


def get_word(pos):
    words = random.sample(list(wn.all_lemma_names(getattr(wn, pos))), 5)
    return [i.replace("_", " ") for i in words]


class Words:
    def __init__(self):
        self.words = {}
        self.get_words()

    def get_words(self):
        logging.info("Getting random words")
        poss = s.PARTS_OF_SPEECH
        for pos in poss:
            self.words[pos] = get_word(pos)
        self.words["VERB"] = [make_3sg_form(i) for i in self.words["VERB"]]


def prepare_fmt(fmt):
    poss = s.PARTS_OF_SPEECH
    for pos in poss:
        op = 0
        while fmt.find(f"{{{pos}}}") != -1:
            fmt = fmt.replace(f"{{{pos}}}", f"{{{pos}[{op}]}}", 1)
            op += 1
    return fmt
