import json
import re


class WordDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_words.json') as f:
            self.dictionary = json.loads(f.read())
            self.punctuation = r"""!"#$%&()*+,-./:;<=>?@[\]^_`{|}~"""

    def is_in_dictionary(self, word):
        return word.translate(str.maketrans('', '', self.punctuation)) in self.dictionary

    def replace_word(self, word):
        punctuation = re.findall(r'[,.?!]+', word)
        temp_word = word.translate(str.maketrans('', '', self.punctuation))
        translated_word = self.dictionary[temp_word].split()[0]
        return translated_word
