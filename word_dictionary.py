import json
import re
import string


class WordDictionary:
    def __init__(self):
        with open('dictionary.json') as f:
            self.dictionary = json.loads(f.read())
        with open('dictionary.json') as f:
            self.symbol_dictionary = json.loads(f.read())

    def is_in_dictionary(self, word):
        return word.translate(str.maketrans('', '', string.punctuation)) in self.dictionary

    def is_in_symbol_dictionary(self, word):
        return word.translate(str.maketrans('', '', string.punctuation)) in self.symbol_dictionary

    def replace_word(self, word):
        punctuation = re.findall(r'[,.?!]+', word)
        temp_word = word.translate(str.maketrans('', '', string.punctuation))
        translated_word = self.dictionary[temp_word].split()
        if punctuation:
            translated_word[-1] += punctuation[0]
        return translated_word

    def replace_symbol(self, symbol):
        punctuation = re.findall(r'[,.?!]+', symbol)
        temp_symbol = symbol.translate(
            str.maketrans('', '', string.punctuation))
        translated_symbol = self.symbol_dictionary[temp_symbol].split()
        if punctuation:
            translated_symbol[-1] += punctuation[0]
        return translated_symbol
