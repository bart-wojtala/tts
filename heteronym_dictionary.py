import json


class HeteronymDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_heteronyms.json') as f:
            self.heteronym_dictionary = json.loads(f.read())

    def is_in_dictionary(self, word):
        return word in self.heteronym_dictionary

    def replace_heteronym(self, word):
        return self.heteronym_dictionary[word]
