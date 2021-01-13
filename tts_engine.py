from models import VoiceMessage, DonationAudio
import sys
import enchant
import math
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
from word_dictionary import WordDictionary


class TextToSpeechEngine:
    available_voices = ['david:',  'gandalf:', 'glados:', 'hal:', 'keanu:', 'msdavid:', 'mszira:',
                        'neil:', 'samuel:', 'satan:', 'stephen:', 'trump:', 'vader:', 'vmail:', 'woman:']
    default_voice = 'keanu:'
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
        self.maximum_word_length = 11
        self.words = []
        self.dictionary = enchant.Dict("en_US")
        self.word_dictionary = WordDictionary()
        self.last_used_voice = ''

        if path:
            # self.words = donation.message.split()
            words_list = donation.message.translate(
                {ord(c): " " for c in "@#$%^&*()[]{};/<>\|`~-=_+"}).split()

            for i, word in enumerate(words_list):
                if not '\'' in word:
                    word_split = re.findall(r'[A-Za-z]+|\d+', word)
                    if len(word_split) > 1:
                        words_list[i:i+1] = word_split

            for i, word in enumerate(words_list):
                if word not in self.available_voices and self.word_dictionary.is_in_dictionary(word):
                    words = self.word_dictionary.replace_word(word)
                    words_list[i:i+1] = words

            self.last_used_voice = ''
            for word in words_list:
                if not self.dictionary.check(word):
                    word_length = len(word)
                    if not self.last_used_voice in self.synth_voices and word_length > self.maximum_word_length and not word in self.available_voices:
                        splits = math.ceil(
                            word_length / self.maximum_word_length)
                        for i in range(0, splits * self.maximum_word_length, self.maximum_word_length):
                            if i != (splits - 1) * self.maximum_word_length:
                                self.words.append(
                                    word[i:i + self.maximum_word_length])
                                if self.last_used_voice == "vader:":
                                    self.words.append(',and')
                                else:
                                    self.words.append(',')
                            else:
                                self.words.append(word[i:])
                    else:
                        if word in self.available_voices:
                            self.last_used_voice = word
                        self.words.append(word)
                else:
                    self.words.append(word)
        else:
            self.words = donation.split()
        self.messages_to_generate = []
        self.sentence_separators = ['.', '?', '!']

        for i in range(0, len(self.words)):
            # if len(''.join(i for i in self.words if i.isalnum())) < 2:
            #     break
            if i == 0 and not self.words[0].endswith(':'):
                if i < len(self.words):
                    self.create_voice_message(i, self.default_voice)
            elif i == 0 and self.words[0].endswith(':'):
                if i < len(self.words):
                    if self.words[i] in self.available_voices:
                        self.create_voice_message(i + 1, self.words[i])
                    else:
                        self.create_voice_message(
                            i + 1, self.default_voice, self.words[0])
            if i != 0 and self.words[i].endswith(':'):
                if self.words[i] in self.available_voices and i < len(self.words):
                    self.create_voice_message(i + 1, self.words[i])

    def create_voice_message(self, start, voice, init_word=''):
        sentence = init_word
        for i in range(start, len(self.words)):
            word = self.words[i]
            if not word in self.available_voices:
                add_word_to_sentence = True
                if word.isdigit() and len(word) > self.maximum_number_length:
                    word = word[0:self.maximum_number_length]
                elif not word.isalpha() and not word.isnumeric() and word.isalnum():
                    add_word_to_sentence = False
                word = word.replace(',', ', ')
                if add_word_to_sentence:
                    if len(sentence) == 0:
                        sentence += word
                    else:
                        sentence += ' ' + word
            else:
                if sentence[-1] not in self.sentence_separators:
                    sentence += '.'
                voice_message = VoiceMessage(voice, sentence)
                self.messages_to_generate.append(voice_message)
                break
            if i == len(self.words) - 1:
                if sentence[-1] not in self.sentence_separators:
                    sentence += '.'
                voice_message = VoiceMessage(voice, sentence)
                self.messages_to_generate.append(voice_message)

    def generate_audio(self):
        if self.messages_to_generate:
            files = []
            if self.use_local_gpu:
                from audio_generator import AudioGenerator
                for index, message in enumerate(self.messages_to_generate):
                    audio_generator = AudioGenerator([message])
                    audio, sampling_rate = audio_generator.generate()
                    file_name = self.write_audio_file(
                        message.voice, audio, sampling_rate)
                    files.append(VoiceMessage(message.voice, file_name))
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
            return DonationAudio(self.donation, files)
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
