import json


class WordDictionary:
    def __init__(self):
        with open('dictionary.json') as f:
            self.dictionary = json.loads(f.read())

    def is_in_dictionary(self, word):
        return word in self.dictionary

    def replace_word(self, word):
        return self.dictionary[word]
