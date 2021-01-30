import json
import re
import string


class SymbolDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_symbols.json') as f:
            self.symbol_dictionary = json.loads(f.read())
            self.key_list = list(self.symbol_dictionary.keys())

    def is_in_dictionary(self, word):
        return word in self.symbol_dictionary

    def contains_symbol(self, word):
        return any(c in word for c in self.key_list)

    def replace_symbol(self, word):
        return self.symbol_dictionary[word]
