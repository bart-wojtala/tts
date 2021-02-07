from models import VoiceMessage, GeneratedAudio
import sys
import enchant
import math
from nltk.tokenize import TweetTokenizer
from nltk.tokenize import word_tokenize
import numpy as np
import re
import requests
import time
from scipy.io.wavfile import write, read
from scipy.signal import lfilter, butter
import soundfile as sf
import pyrubberband as pyrb
from pydub import AudioSegment
from random import randint
from AudioLib import AudioEffect
from textwrap import wrap
from contraction_dictionary import ContractionsDictionary
from symbol_dictionary import SymbolDictionary
from word_dictionary import WordDictionary


class TextToSpeechEngine:
    available_voices = ['carlson:', 'carolla:', 'daria:', 'david:', 'duke:', 'fergy:', 'gandalf:', 'glados:', 'hal:', 'hudson:', 'keanu:', 'mlpab:', 'mlpaj:', 'mlpbm:', 'mlpca:', 'mlpfy:', 'mlpla:', 'mlppp:',
                        'mlprd:', 'mlpry:', 'mlpsb:', 'mlpse:', 'mlpso:', 'mlpte:', 'mlpts:', 'mlpza:', 'msdavid:', 'mszira:', 'nameless:', 'neil:', 'samuel:', 'satan:', 'stephen:', 'trump:', 'vader:', 'vmail:', 'woman:']
    default_voice = 'glados:'
    synth_voices = ["msdavid:", "mszira:", "stephen:"]

    def __init__(self, donation, name, url='', path='', use_local_gpu=False):
        self.donation = donation
        self.name = name
        self.url = url
        self.endpoint_tts = self.url + "/tts"
        self.endpoint_single_tts = self.endpoint_tts + "/single"
        self.path = path
        self.use_local_gpu = use_local_gpu
        self.maximum_number_length = 36
        self.words = []
        self.word_dictionary = WordDictionary()
        self.symbol_dictionary = SymbolDictionary()
        self.contraction_dictionary = ContractionsDictionary()
        self.enchant_dict = enchant.Dict("en_US")
        self.sentence_separators = ['.', '?', '!', ';']
        self.messages_to_generate = []

        if path:
            translated_message = donation.message.translate(
                {ord(c): " " for c in "{}"})
            words_list = translated_message.split()

            if words_list[0] not in self.available_voices:
                words_list.insert(0, self.default_voice)

            voice_indexes = [i for i, word in enumerate(
                words_list) if word in self.available_voices]
            voice_messages = []

            for i, index in enumerate(voice_indexes):
                if i != len(voice_indexes) - 1:
                    voice_message = VoiceMessage(words_list[index], ' '.join(
                        words_list[index+1:voice_indexes[i+1]]), i)
                else:
                    voice_message = VoiceMessage(
                        words_list[index], ' '.join(words_list[index+1:]), i)
                if voice_message.message:
                    voice_messages.append(voice_message)

            for vm in voice_messages:
                message = vm.message.split()
                message_split = []

                for i, word in enumerate(message):
                    if self.contraction_dictionary.is_in_dictionary(word):
                        message_split.append(word)
                    else:
                        tt = TweetTokenizer()
                        words = tt.tokenize(word)
                        for w in words:
                            if w.isalnum() and w != 'bart3s' and w != 'bart3sbot':
                                message_split.extend(
                                    re.findall(r'[A-Za-z]+|\d+', w))
                            elif self.symbol_dictionary.contains_symbol(w) and any(c.isalpha() for c in w):
                                word_split = word_tokenize(w)
                                message_split.extend(word_split)
                            else:
                                message_split.append(w)

                for i, word in enumerate(message_split):
                    if self.symbol_dictionary.is_in_dictionary(word):
                        message_split[i] = self.symbol_dictionary.replace_symbol(
                            word)

                formatted_split = []
                if vm.voice not in self.synth_voices:
                    for i, word in enumerate(message_split):
                        if self.word_dictionary.is_in_dictionary(word):
                            formatted_split.extend(
                                self.word_dictionary.replace_word(word))
                        elif len(word) > 45 and not self.enchant_dict.check(word):
                            word_split = wrap(word, 45)
                            formatted_split.extend(word_split)
                        else:
                            formatted_split.append(word)
                else:
                    formatted_split = message_split

                formatted_message = ' '.join(formatted_split)
                if formatted_message[-1] not in self.sentence_separators:
                    formatted_message += '.'

                new_vm = VoiceMessage(vm.voice, formatted_message, vm.index)
                self.messages_to_generate.append(new_vm)

            for msg in self.messages_to_generate:
                print(msg.message)
        else:
            self.words = donation.split()

    def generate_audio(self):
        if self.messages_to_generate:
            files = []
            if self.use_local_gpu:
                from audio_generator import AudioGenerator
                self.messages_to_generate.sort(
                    key=lambda item: item.voice, reverse=True)

                for index, message in enumerate(self.messages_to_generate):
                    audio_generator = AudioGenerator([message])
                    audio, sampling_rate = audio_generator.generate()
                    file_name = self.write_audio_file(
                        message.voice, audio, sampling_rate)
                    files.append(VoiceMessage(
                        message.voice, file_name, message.index))

                files.sort(key=lambda item: item.index, reverse=False)
            else:
                messages_to_send = []
                single_message = ''
                for index, message in enumerate(self.messages_to_generate):
                    if message.voice == "satan:" or message.voice == "vmail:" or message.voice == "vader:":
                        messages_to_send.append(message)
                    else:
                        single_message += message.voice + ' ' + message.message + ' '
                        if (index == len(self.messages_to_generate) - 1) or (self.messages_to_generate[index + 1].voice == "satan:" or self.messages_to_generate[index + 1].voice == "vmail:" or self.messages_to_generate[index + 1].voice == "vader:"):
                            messages_to_send.append(single_message)
                            single_message = ''

                for message in messages_to_send:
                    if isinstance(message, str):
                        params = {'message': message}
                        audio, sampling_rate = self.request_audio(
                            self.endpoint_single_tts, params)
                        file_name = self.write_audio_file(
                            self.default_voice, audio, sampling_rate)
                        files.append(VoiceMessage(
                            self.default_voice, file_name))
                    else:
                        params = {'voice': message.voice,
                                  'message': message.message}
                        audio, sampling_rate = self.request_audio(
                            self.endpoint_tts, params)
                        file_name = self.write_audio_file(
                            message.voice, audio, sampling_rate)
                        files.append(VoiceMessage(message.voice, file_name))
            return GeneratedAudio(self.donation, files)
        return

    def request_audio(self, endpoint, params):
        response = requests.get(endpoint, params)
        res_json = response.json()
        return np.array(res_json["audio"], dtype=np.int16), res_json["rate"]

    def write_audio_file(self, voice, audio, sampling_rate):
        file_name = self.path + \
            time.strftime("%Y%m%d-%H%M%S_") + self.name + \
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
        elif voice == "vmail:":
            temp_file_name = self.path + "temp.wav"
            write(temp_file_name, sampling_rate, audio)
            fs, audio = read(temp_file_name)
            low_freq = 200.0
            high_freq = 3000.0
            filtered_signal = butter_bandpass_filter(
                audio, low_freq, high_freq, fs, order=6)
            write(file_name, fs, np.array(filtered_signal, dtype=np.int16))
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

    def generate_single_audio(self):
        if self.messages_to_generate:
            from audio_generator import AudioGenerator
            audio_generator = AudioGenerator(self.messages_to_generate)
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
