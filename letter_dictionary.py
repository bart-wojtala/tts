import json


class LetterDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_letters.json') as f:
            self.letter_dictionary = json.loads(f.read())

    def replace_abbreviations(self, message):
        message_split = message.split()
        for i, word in enumerate(message_split):
            if word.isupper():
                message_split[i] = ''.join(
                    self.letter_dictionary[c] if c in self.letter_dictionary else c for c in word)
        return ' '.join(message_split)
