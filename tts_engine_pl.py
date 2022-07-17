import nltk.data


class TextToSpeechEnginePL:
    def __init__(self):
        self.speakers = {}
        with open('filelists/flowtron_speakers.csv') as f:
            for line in f.readlines():
                line_split = line.split('|')
                id = int(line_split[0])
                name = line_split[1].strip()
                self.speakers[name] = id
        self.default_speaker = 'bezi:'
        self.sentence_separators = ['.', '?', '!', ';']
        self.sentence_tokenizer = nltk.data.load(
            'tokenizers/punkt/polish.pickle')

    def preprocess_message(self):
        pass

    def generate_audio(self):
        pass
