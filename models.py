class VoiceMessage:
    def __init__(self, voice, text, index=0):
        self.voice = voice
        self.text = text
        self.index = index


class Message:
    def __init__(self, messageId, name, text, speaker=None, event_type=None):
        self.messageId = messageId
        self.name = name
        self.text = text
        self.event_type = event_type
        self.speaker = speaker


class GeneratedAudio:
    def __init__(self, message, files):
        self.message = message
        self.files = files
        self.length = len(files)
