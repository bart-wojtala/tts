from models import VoiceMessage, GeneratedAudio
import nltk.data
import re
import time
from scipy.io.wavfile import write, read
from scipy.signal import lfilter, butter
import soundfile as sf
import pyrubberband as pyrb
from pydub import AudioSegment
from random import randint
from AudioLib import AudioEffect
from textwrap import wrap
from dictionary import ContractionsDictionary, EmoteDictionary, EmoticonDictionary, HeteronymDictionary, LetterDictionary, SymbolDictionary, WordDictionary
from audio_generator import AudioGenerator
import emoji


class TextToSpeechEngine:
    available_voices = ['biggie:', 'carlson:', 'daria:', 'david:', 'duke:', 'gandalf:', 'glados:', 'hal:', 'hudson:', 'johnny:', 'keanu:', 'mlpab:', 'mlpaj:',
                        'mlpca:', 'mlpfy:', 'mlppp:', 'mlprd:', 'mlpts:', 'mlpza:', 'msdavid:', 'neil:', 'samuel:', 'satan:', 'stephen:', 'trevor:', 'trump:', 'vader:', 'woman:']
    default_voice = 'glados:'
    synth_voices = ['msdavid:', 'stephen:']

    def __init__(self, path=''):
        self.path = path
        self.maximum_number_length = 36
        self.word_dictionary = WordDictionary()
        self.symbol_dictionary = SymbolDictionary()
        self.contraction_dictionary = ContractionsDictionary()
        self.emote_dictionary = EmoteDictionary()
        self.emoticon_dictionary = EmoticonDictionary()
        self.heteronym_dictionary = HeteronymDictionary()
        self.letter_dictionary = LetterDictionary()
        self.sentence_separators = ['.', '?', '!', ';']
        self.sentence_tokenizer = nltk.data.load(
            'tokenizers/punkt/english.pickle')

    def preprocess_message(self, donation):
        translated_message = donation.text.translate(
            {ord(c): " " for c in "{}"})
        words_list = translated_message.split()

        if words_list[0] not in self.available_voices:
            words_list.insert(0, self.default_voice)

        voice_indexes = [i for i, word in enumerate(
            words_list) if word in self.available_voices]
        voice_messages = []

        for i, index in enumerate(voice_indexes):
            text = ' '.join(words_list[index+1:voice_indexes[i+1]]) if i != len(
                voice_indexes) - 1 else ' '.join(words_list[index+1:])
            if text:
                voice = words_list[index]
                vm = VoiceMessage(voice, self.format_message(voice, text), i)
                voice_messages.append(vm)

        return voice_messages

    def replace_symbols_and_emojis(self, message):
        message = emoji.demojize(message)
        message = self.emoticon_dictionary.replace_emoticons(message)
        message = self.emote_dictionary.replace_emotes(message)
        message = self.letter_dictionary.replace_abbreviations(message)
        message_as_list = list(message)
        for i, c in enumerate(message_as_list):
            if not c.isalnum() and self.symbol_dictionary.contains_symbol(c):
                message_as_list[i] = self.symbol_dictionary.replace_symbol(c)
        message = ''.join(message_as_list).replace('  ', ' ').strip()
        return message

    def format_message(self, voice, message):
        message = self.replace_symbols_and_emojis(message)
        sentences = [s for s in self.sentence_tokenizer.tokenize(message)]
        new_sentences = []
        for sentence in sentences:
            words = sentence.split()
            for i, word in enumerate(words):
                if not self.contraction_dictionary.is_in_dictionary(word):
                    word_split = re.findall(r"[A-Za-z]+|[-+]?[\d.\d]+|\S", word)
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

    def generate_audio(self, donation):
        messages_to_generate = self.preprocess_message(donation)
        if messages_to_generate:
            files = []
            messages_to_generate.sort(
                key=lambda item: item.voice, reverse=True)

            for message in messages_to_generate:
                audio_generator = AudioGenerator([message])
                audio, sampling_rate = audio_generator.generate()
                file_name = self.write_audio_file(
                    donation.name, message.voice, audio, sampling_rate)
                files.append(VoiceMessage(
                    message.voice, file_name, message.index))

            files.sort(key=lambda item: item.index, reverse=False)
            return GeneratedAudio(donation, files)
        return

    def write_audio_file(self, name, voice, audio, sampling_rate):
        file_name = self.path + \
            time.strftime("%Y%m%d-%H%M%S_") + name + \
            str(randint(0, 100)) + ".wav"
        if voice == "satan:":
            temp_file_name = self.path + "temp.wav"
            write(temp_file_name, sampling_rate, audio)

            fixed_framerate = 11000
            sound = AudioSegment.from_file(temp_file_name)
            sound = sound.set_frame_rate(fixed_framerate)
            write(file_name, fixed_framerate, audio)

            y, sr = sf.read(file_name)
            y_stretch = pyrb.time_stretch(y, sr, 1.6)
            y_shift = pyrb.pitch_shift(y, sr, 1.6)
            sf.write(file_name, y_stretch, sr, format='wav')

            sound = AudioSegment.from_wav(file_name)
            sound.export(file_name, format="wav")
        elif voice == "vader:":
            temp_file_name = self.path + "temp.wav"
            write(temp_file_name, sampling_rate, audio)
            AudioEffect.robotic(temp_file_name, file_name)

            y, sr = sf.read(file_name)
            y_stretch = pyrb.time_stretch(y, sr, 0.9)
            y_shift = pyrb.pitch_shift(y, sr, 0.9)
            sf.write(file_name, y_stretch, sr, format='wav')

            sound = AudioSegment.from_wav(file_name)
            sound.export(file_name, format="wav")
        else:
            write(file_name, sampling_rate, audio)
        return file_name

    def generate_single_audio(self, messages_to_generate):
        if messages_to_generate:
            audio_generator = AudioGenerator(messages_to_generate)
            return audio_generator.generate()
        return


def butter_params(low_freq, high_freq, fs, order=5):
    nyq = 0.5 * fs
    low = low_freq / nyq
    high = high_freq / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, low_freq, high_freq, fs, order=5):
    b, a = butter_params(low_freq, high_freq, fs, order=order)
    y = lfilter(b, a, data)
    return y
