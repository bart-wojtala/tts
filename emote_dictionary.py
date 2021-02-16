import json


class EmoteDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_emotes.json') as f:
            self.emote_dictionary = json.loads(f.read())

    def is_in_dictionary(self, word):
        return list(filter(word.startswith, self.emote_dictionary)) != []

    def replace_emote(self, word):
        key = list(filter(word.startswith, self.emote_dictionary))[0]
        return [self.emote_dictionary[key], word.split(key)[1]]
