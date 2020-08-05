from models import VoiceMessage
from audio_generator import AudioGenerator
from marshmallow import Schema, fields

class TextToSpeechEngine:
    available_voices = ['woman:', 'david:', 'neil:', 'stephen:']
    default_voice = 'woman:'

    def __init__(self, donation_message):
        words = donation_message.split()
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
            audio_generator = AudioGenerator(self.messages_to_generate)
            return audio_generator.generate()
        return

class AudioSchema(Schema):
    audio = fields.Str()
    rate = fields.Str()
