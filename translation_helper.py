from deep_translator import GoogleTranslator
import settings as s
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def g_translate(lang, text):
    return GoogleTranslator(target=lang).translate(text)


class Translations:
    def __init__(self, texter, languages):
        self.languages = languages
        self.texter = texter
        self.texts = {
            "en":
                {
                    "query": self.texter.query,
                    "result": self.texter.open_ai_result
                }
        }
        self.generate_translations(self.languages)

    def generate_translations(self, languages):
        logging.info("Translating languages")
        for lang in list(filter(lambda x: x != "en", languages)):
            self.texts[lang]["query"] = g_translate(lang, self.texter.query)
            self.texts[lang]["result"] = g_translate(lang, self.texter.open_ai_result)
            logging.info(f"{lang}..DONE")
        logging.info("Translations generated")
