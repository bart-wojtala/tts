import json
import re


class AbbreviationDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_letters.json') as f:
            self.dictionary = json.loads(f.read())
            self.punctuation = r"""!"#$%&()*+,-./:;<=>?@[\]^_`{|}~"""

    def is_abbreviation(self, word):
        translated_word = word.translate(
            str.maketrans('', '', self.punctuation))
        return translated_word.isupper() and translated_word.isalpha()

    def replace_abbreviation(self, word):
        punctuation = re.findall(r'[,.?!]+', word)
        temp_word = word.translate(str.maketrans('', '', self.punctuation))
        translated_word = self.dictionary[temp_word].split()
        if punctuation:
            translated_word[-1] += punctuation[0]
        return translated_word
