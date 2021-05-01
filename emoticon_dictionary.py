import json


class EmoticonDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_emoticons.json') as f:
            self.emoticon_dictionary = json.loads(f.read())

    def contains_emoticons(self, message):
        if any(emoticon in message for emoticon in self.emoticon_dictionary.keys()):
            return True
        return False

    def replace_emoticons(self, message):
        for key in self.emoticon_dictionary:
            message = message.replace(key, self.emoticon_dictionary[key])
        return message
