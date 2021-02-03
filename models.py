class VoiceMessage:
    def __init__(self, voice, message, index=0):
        self.voice = voice
        self.message = message
        self.index = index


class Donation:
    def __init__(self, messageId, name, message):
        self.messageId = messageId
        self.name = name
        self.message = message


class GeneratedAudio:
    def __init__(self, donation, files):
        self.donation = donation
        self.files = files
        self.length = len(files)


class AudioSequence:
    def __init__(self, audio, rate):
        self.audio = audio
        self.rate = rate
