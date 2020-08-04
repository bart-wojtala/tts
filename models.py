class VoiceMessage:
    def __init__(self, voice, message):
        self.voice = voice
        self.message = message

class Donation:
    def __init__(self, name, message):
        self.name = name
        self.message = message
        
class DonationAudio:
    def __init__(self, donation, file):
        self.donation = donation
        self.file = file

class AudioSequence:
    def __init__(self, audio, rate):
        self.audio = audio
        self.rate = rate
