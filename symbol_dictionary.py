import json
import re
import string


class SymbolDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_symbols.json') as f:
            self.symbol_dictionary = json.loads(f.read())

    def is_in_dictionary(self, word):
        return word in self.symbol_dictionary

    def replace_symbol(self, word):
        return self.symbol_dictionary[word]
