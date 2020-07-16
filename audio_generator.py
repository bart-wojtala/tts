from datetime import datetime
from scipy.io.wavfile import write

import numpy as np
import torch

import os
import sys
sys.path.append('tts/')
sys.path.append('tts/waveglow/')
from hparams import create_hparams
from model import Tacotron2
from layers import TacotronSTFT, STFT
from audio_processing import griffin_lim
from train import load_model
from text import text_to_sequence

class AudioGenerator:
    models = {
        "david:": "attenborough_checkpoint_547000",
        "neil:": "neil_tyson_checkpoint_500000"
    }

    def __init__(self, name, messages):
        self.name = name
        self.messages = messages

    def generate(self):
        hparams = create_hparams()
        hparams.sampling_rate = 22050
        models_path = "tts/models/"
        generated_audio_path = "generated_audio/"
        if not os.path.exists(generated_audio_path):
            os.makedirs(generated_audio_path)

        waveglow_path = models_path + 'waveglow_256channels.pt'
        waveglow = torch.load(waveglow_path)['model']
        waveglow.cuda().eval().half()
        for k in waveglow.convinv:
            k.float()

        joined_audio = np.empty(1,)
        silence = np.zeros(11000,)
        for message in self.messages:
            print(message.voice, message.message)
            if len(message.message) > 127:
                hparams.max_decoder_steps=100000
            else:
                hparams.max_decoder_steps=10000

            model = load_model(hparams)
            model.load_state_dict(torch.load(models_path + self.models[message.voice])['state_dict'])
            _ = model.cuda().eval().half()

            sequence = np.array(text_to_sequence(message.message, ['english_cleaners']))[None, :]
            sequence = torch.autograd.Variable(
                torch.from_numpy(sequence)).cuda().long()

            mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)

            with torch.no_grad():
                audio = waveglow.infer(mel_outputs_postnet, sigma=0.666)
            audio_data = audio[0].data.cpu().numpy()
            
            audio_data = np.concatenate((audio_data, silence))
            scaled_audio = np.int16(audio_data/np.max(np.abs(audio_data)) * 32767)
            joined_audio = np.concatenate((joined_audio, scaled_audio))

            torch.cuda.empty_cache()
            
        scaled_audio = np.int16(joined_audio/np.max(np.abs(joined_audio)) * 32767)
        file_name = generated_audio_path + "audio_" + str(datetime.timestamp(datetime.now())) + "_" + self.name + ".wav"
        write(file_name, hparams.sampling_rate, scaled_audio)
        return file_name
