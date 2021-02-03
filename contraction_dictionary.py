import json


class ContractionsDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_contractions.json') as f:
            self.contraction_dictionary = json.loads(f.read())

    def is_in_dictionary(self, word):
        return word in self.contraction_dictionary or word.replace("’", "'") in self.contraction_dictionary

    def replace_symbol(self, word):
        return self.contraction_dictionary[word]
