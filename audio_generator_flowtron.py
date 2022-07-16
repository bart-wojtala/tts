import os
import sys
sys.path.append('flowtron')
sys.path.append('tacotron2/waveglow/')
from data import Data
from flowtron import Flowtron
import torch
import json


class AudioGeneratorFlowtron:
    models = {
        'flowtron': 'flowtron_model.pt',
    }

    waveglow = {
        'default': 'waveglow_256channels_universal_v5.pt'
    }

    def __init__(self):
        self.config_path = 'flowtron/config.json'
        self.models_path = os.getcwd() + '/models/'
        self.training_files_path = os.getcwd() + '/filelists/dataset_train.txt'
        with open(self.config_path) as f:
            data = f.read()
        self.config = json.loads(data)
        self.config['model_config']['n_speakers'] = 41
        self.lambd = 0.001
        self.sigma = 0.85
        self.waveglow_sigma = 1
        self.n_frames = 1800
        self.aggregation_type = 'batch'

        self.model = Flowtron(**self.config['model_config']).cuda()
        flowtron_path = self.models_path + self.models['flowtron']
        waveglow_path = self.models_path + self.waveglow['default']

        if 'state_dict' in torch.load(flowtron_path, map_location='cpu'):
            load = torch.load(flowtron_path, map_location='cpu')
            state_dict = load['state_dict']
        else:
            load = torch.load(flowtron_path, map_location='cpu')
            state_dict = load['model'].state_dict()
        self.model.load_state_dict(state_dict, strict=False)
        self.model.eval()

        self.waveglow = torch.load(waveglow_path)['model']
        self.waveglow.cuda().eval()

        self.z_baseline = torch.cuda.FloatTensor(
            1, 80, self.n_frames).normal_() * self.sigma

        ignore_keys = ['training_files', 'validation_files']
        self.trainset = Data(
            self.training_files_path,
            **dict((k, v) for k, v in self.config['data_config'].items() if k not in ignore_keys))

    def generate(self, text: str, speaker: int):
        speaker_vecs = self.trainset.get_speaker_id(speaker).cuda()
        speaker_vecs = speaker_vecs[None]
        text = self.trainset.get_text(text).cuda()
        text = text[None]

        with torch.no_grad():
            mel_baseline = self.model.infer(
                self.z_baseline, speaker_vecs, text)[0]

        with torch.no_grad():
            audio_base = self.waveglow.infer(
                mel_baseline, sigma=self.waveglow_sigma)

        audio = audio_base[0].data.cpu().numpy()
        return audio

    def prepare_dataset(self, dataset_path):
        dataset = Data(
            dataset_path,
            **dict((k, v) for k, v in self.config['data_config'].items() if k not in ['training_files', 'validation_files']))
        return dataset
