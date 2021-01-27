import json
import re
import string


class WordDictionary:
    def __init__(self):
        with open('dictionaries/dictionary.json') as f:
            self.dictionary = json.loads(f.read())

    def is_in_dictionary(self, word):
        return word.translate(str.maketrans('', '', string.punctuation)) in self.dictionary

    def replace_word(self, word):
        punctuation = re.findall(r'[,.?!]+', word)
        temp_word = word.translate(str.maketrans('', '', string.punctuation))
        translated_word = self.dictionary[temp_word].split()
        if punctuation:
            translated_word[-1] += punctuation[0]
        return translated_word
