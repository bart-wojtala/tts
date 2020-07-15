from models import VoiceMessage

class TextToSpeechEngine:
    available_voices = ['david:', 'neil:']

    def __init__(self, name, donation_message):
        self.name = name
        words = donation_message.split()
        messages_to_generate = []

        for i in range(0, len(words)):
            sentence = ''
            voice = ''
            if words[i].endswith(':'):
                if words[i] in self.available_voices and i < len(words):
                    voice = words[i]
                    for j in range(i + 1, len(words)):
                        if not words[j] in self.available_voices:
                            if len(sentence) == 0:
                                sentence += words[j]
                            else:
                                sentence += ' ' + words[j]
                        else:
                            if sentence[-1] != '.':
                                sentence += '.'
                            voice_message = VoiceMessage(voice, sentence)
                            messages_to_generate.append(voice_message)
                            break
                        if j == len(words) - 1:
                            if sentence[-1] != '.':
                                sentence += '.'
                            voice_message = VoiceMessage(voice, sentence)
                            messages_to_generate.append(voice_message)
        self.messages_to_generate = messages_to_generate
    
    def get_messages(self):
        return self.messages_to_generate
