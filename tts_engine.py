from models import VoiceMessage, DonationAudio
# from audio_generator import AudioGenerator
import numpy as np
import requests
import time
from scipy.io.wavfile import write
import soundfile as sf
import pyrubberband as pyrb
from pydub import AudioSegment

class TextToSpeechEngine:
    available_voices = ['woman:', 'david:', 'neil:', 'stephen:', 'satan:']
    default_voice = 'woman:'

    def __init__(self, donation, url, path):
        self.donation = donation
        self.name = donation.name
        self.url = url
        self.path = path
        words = donation.message.split()
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
            i = 0
            for message in self.messages_to_generate:
                params = {'voice': message.voice, 'message': message.message}
                response = requests.get(self.url, params)
                res_json = response.json()
                audio = np.array(res_json["audio"], dtype=np.int16)
                sampling_rate = res_json["rate"]

                file_name = self.path + time.strftime("%Y%m%d-%H%M%S_") + self.name + str(i) + ".wav"
                if message.voice == "satan:":
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
                else:
                    write(file_name, sampling_rate, audio)
                files.append(file_name)
                i += 1
            return DonationAudio(self.donation, files)
            # audio_generator = AudioGenerator(self.messages_to_generate)
            # return audio_generator.generate()
        return
