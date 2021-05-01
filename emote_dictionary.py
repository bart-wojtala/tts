import json


class EmoteDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_emotes.json') as f:
            self.emote_dictionary = json.loads(f.read())

    def replace_emotes(self, message):
        message_split = message.split()
        for i, word in enumerate(message_split):
            if word.lower().strip() in self.emote_dictionary:
                message_split[i] = self.emote_dictionary[word.lower().strip()]
        return ' '.join(message_split)
