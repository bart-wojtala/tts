import json
import re


class AbbreviationDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_letters.json') as f:
            self.dictionary = json.loads(f.read())
            self.punctuation = r"""!"#$%&()*+,-./:;<=>?@[\]^_`{|}~"""

    def is_abbreviation(self, word):
        translated_word = word.translate(
            str.maketrans('', '', self.punctuation))
        return translated_word.isupper() and translated_word.isalpha()

    def replace_abbreviation(self, word):
        punctuation = re.findall(r'[,.?!]+', word)
        temp_word = word.translate(str.maketrans('', '', self.punctuation))
        translated_word = self.dictionary[temp_word].split()
        if punctuation:
            translated_word[-1] += punctuation[0]
        return translated_word


class ContractionsDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_contractions.json') as f:
            self.contraction_dictionary = json.loads(f.read())

    def is_in_dictionary(self, word):
        return word in self.contraction_dictionary or word.replace("’", "'") in self.contraction_dictionary

    def replace_symbol(self, word):
        return self.contraction_dictionary[word]


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


class HeteronymDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_heteronyms.json') as f:
            self.heteronym_dictionary = json.loads(f.read())

    def is_in_dictionary(self, word):
        return word in self.heteronym_dictionary

    def replace_heteronym(self, word):
        return self.heteronym_dictionary[word]


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


class WordDictionary:
    def __init__(self):
        with open('dictionaries/dictionary_words.json') as f:
            self.dictionary = json.loads(f.read())
            self.punctuation = r"""!"#$%&()*+,-./:;<=>?@[\]^_`{|}~"""

    def is_in_dictionary(self, word):
        return word.translate(str.maketrans('', '', self.punctuation)) in self.dictionary

    def replace_word(self, word):
        punctuation = re.findall(r'[,.?!]+', word)
        temp_word = word.translate(str.maketrans('', '', self.punctuation))
        translated_word = self.dictionary[temp_word].split()[0]
        return translated_word
