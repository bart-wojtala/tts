class VoiceMessage:
    def __init__(self, voice, message, index=0):
        self.voice = voice
        self.message = message
        self.index = index


class Donation:
    def __init__(self, messageId, name, message, event_type=None):
        self.messageId = messageId
        self.name = name
        self.message = message
        self.event_type = event_type


class GeneratedAudio:
    def __init__(self, donation, files):
        self.donation = donation
        self.files = files
        self.length = len(files)
