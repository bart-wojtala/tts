import json
import re
import string


class ContractionsDictionary:
    def __init__(self):
        with open('dictionaries/contraction_dictionary.json') as f:
            self.contraction_dictionary = json.loads(f.read())

    def is_in_dictionary(self, word):
        print(word)
        return word in self.contraction_dictionary

    def replace_symbol(self, word):
        return self.contraction_dictionary[word]
