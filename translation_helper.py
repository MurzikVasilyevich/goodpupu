from deep_translator import GoogleTranslator
import settings as s
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def g_translate(lang, text):
    return GoogleTranslator(target=lang).translate(text)


class Translations:
    def __init__(self, gen):
        self.languages = s.LANGUAGES
        self.gen = gen
        self.texts = {"en_q": self.gen.query, "en": self.gen.open_ai_result}
        self.generate_translations()

    def generate_translations(self):
        logging.info("Translating languages")
        for lang in list(filter(lambda x: x != "en", self.languages)):
            self.texts[f"{lang}_q"] = g_translate(lang, self.gen.query)
            self.texts[lang] = g_translate(lang, self.gen.open_ai_result)
            logging.info(f"{lang}..DONE")