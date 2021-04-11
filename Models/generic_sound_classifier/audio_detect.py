import h5py
import librosa
import numpy as np
import pandas as pd
import torch
import io
from Models.generic_sound_classifier import models_code as models

class AudioClassifier:
    def __init__(self):
        # parameters
        self.CHANNELS = 1            # channels of recordings
        self.RATE = 32000            # sample rate
        self.REC_BUFFER_SIZE = 1024  # recorder buffer size, every records has channel's number of samples, if channel = 2, each record has 2 samples
                                # this parameter also determines the delay between recording and playback, LEN_REC_BUFFER / RATE (s) is the actual delay
        self.chunk_len = 62          # 62 * REC_BUFFER_SIZE / RATE, approximately 2 (s) data for inference        (*algorithm cost*)
        self.chunk_hs =  10          # 7 * REC_BUFFER_SIZE / RATE, approximately 1280 (ms), chunk level hop size   (*algorithm cost*)

        self.nfft = 1024             # nfft for stft
        self.hsfft = 500             # hsfft for fft hop size
        self.chunk_stft_len = 128    # neural network time axis
        self.mel_bins = 64           # neural network frequency axis
        self.window = 'hann'
        self.fmin = 50
        self.fmax = 14000

        self.cuda = False

        self.model_dir = 'Models/generic_sound_classifier/models/'
        self.model_path = self.model_dir + 'Cnn9_GMP_64x64_300000_iterations_mAP=0.37.pth'
        # self.model_path = self.model_dir + 'Cnn13_GMP_64x64_520000_iterations_mAP=0.42.pth'
        self.scalar_fn = self.model_dir + 'scalar.h5'
        self.csv_fname = self.model_dir + 'validate_meta.csv'

        self.melW = librosa.filters.mel( sr=self.RATE,
                            n_fft=self.nfft,
                            n_mels=self.mel_bins,
                            fmin=self.fmin,
                            fmax=self.fmax)
        self.mean = []
        self.std = []
        with h5py.File(self.scalar_fn, 'r') as hf:
            self.mean = hf['mean'][:]
            self.std = hf['std'][:]
        
        checkpoint = torch.load(self.model_path, map_location=lambda storage, loc: storage)
        self.model = models.Cnn9_GMP_64x64(527)
        # self.model = models.Cnn13_GMP_64x64(527)
        self.model.load_state_dict(checkpoint['model'])
        if self.cuda:
            self.model.cuda()
        
    def logmel_extract(self,data):
        S = np.abs(librosa.stft(y=data,
                                n_fft=self.nfft,
                                hop_length=self.hsfft,
                                center=True,
                                window=self.window,
                                pad_mode='reflect'))**2

        mel_S = np.dot(self.melW, S).T
        log_mel_S = librosa.power_to_db(mel_S, ref=1.0, amin=1e-10, top_db=None)

        return log_mel_S 

    def load_class_label_indices(self,class_labels_indices_path):    
        df = pd.read_csv(class_labels_indices_path, sep=',')
        labels = df['display_name'].tolist()
        lb_to_ix = {lb: i for i, lb in enumerate(labels)}
        ix_to_lb = {i: lb for i, lb in enumerate(labels)}    
        return labels, lb_to_ix, ix_to_lb

    def inference(self, x):
        '''

        Inference output for single instance from neural network
        '''
        x = torch.Tensor(x).view(1, x.shape[0], x.shape[1])
        if self.cuda:
            x = x.cuda()
        
        with torch.no_grad():
            self.model.eval()
            y = self.model(x)

        prob = y.data.cpu().numpy().squeeze(axis=0)
        predict_idxs = prob.argsort()[-6:][::-1]
        predict_probs = prob[predict_idxs]
        return predict_idxs, predict_probs

    def detect(self,data):
        data = data.reshape(-1,)
        x = self.logmel_extract(data)
        x = (x - self.mean)/self.std
        _, _, ix_to_lb = self.load_class_label_indices(self.csv_fname)
        predict_idxs, predict_probs = self.inference(x)
        predict_labels = []
        for idx in predict_idxs:
            predict_labels.append(ix_to_lb[idx])
        return predict_labels