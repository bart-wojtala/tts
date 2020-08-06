from models import VoiceMessage, DonationAudio
# from audio_generator import AudioGenerator
import sys
import numpy as np
import requests
import time
from scipy.io.wavfile import write, read
from scipy.signal import lfilter, butter
import soundfile as sf
import pyrubberband as pyrb
from pydub import AudioSegment
from random import randint

class TextToSpeechEngine:
    available_voices = ['woman:', 'david:', 'neil:', 'stephen:', 'satan:', 'voicemail:', 'darthvader:']
    default_voice = 'woman:'

    def __init__(self, donation, name, url, path):
        self.donation = donation
        self.name = name
        self.url = url
        self.endpoint_tts = self.url + "/tts"
        self.endpoint_single_tts = self.url + "/singletts"
        self.path = path
        if path:
            words = donation.message.split()
        else:
            words = donation.split()
        messages_to_generate = []
        sentence_separators = ['.', '?', '!']

        for i in range(0, len(words)):
            sentence = ''
            voice = ''
            if i == 0 and not words[0].endswith(':'):
                if i < len(words):
                    voice = self.default_voice
                    for j in range(i, len(words)):
                        word = words[j]
                        if not word in self.available_voices:
                            if word.isdigit() and len(word) > 36:
                                word = word[0:36]
                            word = word.replace(',', ', ')
                            if len(sentence) == 0:
                                sentence += word
                            else:
                                sentence += ' ' + word
                        else:
                            if sentence[-1] not in sentence_separators:
                                sentence += '.'
                            voice_message = VoiceMessage(voice, sentence)
                            messages_to_generate.append(voice_message)
                            break
                        if j == len(words) - 1:
                            if sentence[-1] not in sentence_separators:
                                sentence += '.'
                            voice_message = VoiceMessage(voice, sentence)
                            messages_to_generate.append(voice_message)
            if words[i].endswith(':'):
                if words[i] in self.available_voices and i < len(words):
                    voice = words[i]
                    for j in range(i + 1, len(words)):
                        word = words[j]
                        if not word in self.available_voices:
                            if word.isdigit() and len(word) > 36:
                                word = word[0:36]
                            word = word.replace(',', ', ')
                            if len(sentence) == 0:
                                sentence += word
                            else:
                                sentence += ' ' + word
                        else:
                            if sentence[-1] not in sentence_separators:
                                sentence += '.'
                            voice_message = VoiceMessage(voice, sentence)
                            messages_to_generate.append(voice_message)
                            break
                        if j == len(words) - 1:
                            if sentence[-1] not in sentence_separators:
                                sentence += '.'
                            voice_message = VoiceMessage(voice, sentence)
                            messages_to_generate.append(voice_message)
        self.messages_to_generate = messages_to_generate

    def generate_audio(self):
        if self.messages_to_generate:
            files = []
            messages_to_send = []
            single_message = ''
            for index, message in enumerate(self.messages_to_generate):
                if message.voice == "darthvader:" or message.voice == "voicemail:":
                    messages_to_send.append(message)
                else:
                    single_message += message.voice + ' ' + message.message + ' '
                    if (index == len(self.messages_to_generate) - 1) or (self.messages_to_generate[index + 1].voice == "darthvader:" or self.messages_to_generate[index + 1].voice == "voicemail:"):
                        messages_to_send.append(single_message)
                        single_message = ''

            for message in messages_to_send:
                if(isinstance(message, str)):
                    params = {'message': message}
                    response = requests.get(self.endpoint_single_tts, params)
                    res_json = response.json()
                    audio = np.array(res_json["audio"], dtype=np.int16)
                    sampling_rate = res_json["rate"]
                    file_name = self.request_audio(self.default_voice, audio, sampling_rate)
                    files.append(VoiceMessage(self.default_voice, file_name))
                else:
                    params = {'voice': message.voice, 'message': message.message}
                    response = requests.get(self.endpoint_tts, params)
                    res_json = response.json()
                    audio = np.array(res_json["audio"], dtype=np.int16)
                    sampling_rate = res_json["rate"]
                    file_name = self.request_audio(message.voice, audio, sampling_rate)
                    files.append(VoiceMessage(message.voice, file_name))
            return DonationAudio(self.donation, files)
            # audio_generator = AudioGenerator(self.messages_to_generate)
            # return audio_generator.generate()
        return

    def request_audio(self, voice, audio, sampling_rate):
        file_name = self.path + time.strftime("%Y%m%d-%H%M%S_") + self.name + str(randint(0, 100)) + ".wav"
        if voice == "satan:":
            temp_file_name = "generated_audio/test.wav"
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
        elif voice == "voicemail:":
            temp_file_name = self.path + "test.wav"
            write(temp_file_name, sampling_rate, audio)
            fs,audio = read("generated_audio/test.wav")
            low_freq = 200.0
            high_freq = 3000.0
            filtered_signal = butter_bandpass_filter(audio, low_freq, high_freq, fs, order=6)
            write(file_name, fs, np.array(filtered_signal, dtype = np.int16))
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
