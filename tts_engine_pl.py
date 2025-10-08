from models import GeneratedAudio, Message, VoiceMessage
import nltk.data
from audio_generator_flowtron import AudioGeneratorFlowtron


class TextToSpeechEnginePL:
    def __init__(self):
        self.speakers = {}
        with open('filelists/flowtron_speakers.csv') as f:
            for line in f.readlines():
                line_split = line.split('|')
                id = int(line_split[0])
                name = line_split[1].strip()
                self.speakers[name] = id
        self.default_speaker = 'bezi:'
        self.sentence_separators = ['.', '?', '!', ';']
        self.sentence_tokenizer = nltk.data.load(
            'tokenizers/punkt/polish.pickle')

    def preprocess_message(self, text):
        voice_messages = []
        print(text)
        translated_text = text.translate({ord(c): " " for c in "{}"})
        print(translated_text)
        words_list = translated_text.split()
        print(words_list)
        if words_list[0] not in self.speakers.keys():
            words_list.insert(0, self.default_speaker)

        voice_indexes = [i for i, word in enumerate(
            words_list) if word in self.speakers.keys()]

        for i, idx in enumerate(voice_indexes):
            text = ' '.join(words_list[idx+1:voice_indexes[i+1]]) if i != len(
                voice_indexes) - 1 else ' '.join(words_list[idx+1:])
            if text:
                voice = words_list[idx]

                # At the beginning of each sentence add duplicated first character
                # vm = VoiceMessage(voice, self.format_message(voice, text), i)
                # voice_messages.append(vm)

        return voice_messages

    def format_message(self, voice, message):
        message = self.replace_symbols_and_emojis(message)
        sentences = [s for s in self.sentence_tokenizer.tokenize(message)]
        new_sentences = []
        for sentence in sentences:
            words = sentence.split()
            for i, word in enumerate(words):
                if not self.contraction_dictionary.is_in_dictionary(word):
                    word_split = re.findall(
                        r"[A-Za-z]+|[-+]?[\d.\d]+|\S", word)
                    for j, w in enumerate(word_split):
                        if len(w) > 1 and re.match(r"[-+]?[\d]*[.\d]+", w):
                            groups = re.findall('(.\d+)', w)
                            for group in groups:
                                if '.' in group:
                                    group_list = list(group)
                                    group_list[0] = ' point'
                                    w = w.replace(group, ' '.join(group_list))

                            word_split[j] = w.replace(
                                '+', ' plus ').replace('-', ' minus ').strip()
                        else:
                            if self.word_dictionary.is_in_dictionary(w):
                                word_split[j] = self.word_dictionary.replace_word(
                                    word)

                        if (voice not in self.synth_voices) and (len(word) > 45):
                            word_split[j] = ' '.join(wrap(w, 45))

                    words[i] = ''.join(word_split)

            for i, word in enumerate(words):
                if word.isdigit() and len(word) > self.maximum_number_length:
                    words[i] = word[:self.maximum_number_length]

            formatted_sentence = ' '.join(words)
            if formatted_sentence[-1] not in self.sentence_separators:
                formatted_sentence += '.'
            new_sentences.append(formatted_sentence)
        return ' '.join(new_sentences)

    def generate_audio(self, message: Message):
        text = message.text
        text = self.preprocess_message(text)
        audio_generator = AudioGeneratorFlowtron()
        print(text)
        return audio_generator.generate('Do widzenia panie jarku.', 0)
