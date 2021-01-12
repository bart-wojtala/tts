import json
import re
import string


class WordDictionary:
    def __init__(self):
        with open('dictionary.json') as f:
            self.dictionary = json.loads(f.read())

    def is_in_dictionary(self, word):
        return word.translate(str.maketrans('', '', string.punctuation)) in self.dictionary

    def replace_word(self, word):
        punctuation = re.findall(r'[,.?!]+', word)
        temp_word = word.translate(str.maketrans('', '', string.punctuation))
        return self.dictionary[temp_word].split() + punctuation
