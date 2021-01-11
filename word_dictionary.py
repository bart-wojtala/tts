import json


class WordDictionary:
    def __init__(self):
        with open('dictionary.json') as f:
            self.dictionary = json.loads(f.read())

    def replace_word(self, word):
        return word
