class VoiceMessage:
    def __init__(self, voice, message):
        self.voice = voice
        self.message = message

class Donation:
    def __init__(self, name, message):
        self.name = name
        self.message = message
        
class DonationAudio:
    def __init__(self, donation, sequence):
        self.donation = donation
        self.sequence = sequence

class AudioSequence:
    def __init__(self, audio_list, length):
        self.audio_list = audio_list
        self.length = length
