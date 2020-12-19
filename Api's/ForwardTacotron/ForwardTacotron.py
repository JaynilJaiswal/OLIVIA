#!/usr/bin/env python
# coding: utf-8

# # Forward Tacotron 2 for Text-to-speech conversion 
# ## This one needs needs 940Mb(decent) memory, runs on GPU, is  very fast and quality really good but needs no preprocessing

# In[1]:


import os
from os.path import exists, join, basename, splitext

# # Clone the repo including pretrained models
# if not exists("ForwardTacotron"):
#     get_ipython().system('git clone https://github.com/as-ideas/ForwardTacotron.git')

# # Install requirements
# get_ipython().run_line_magic('cd', '../ForwardTacotron/')
#!apt-get install espeak
# !pip install -r requirements.txt

# Load pretrained models
from notebook_utils.synthesize import (
    get_forward_model, get_melgan_model, get_wavernn_model, synthesize, init_hparams)
from utils import hparams as hp
import IPython.display as ipd
init_hparams('notebook_utils/pretrained_hparams.py')
tts_model = get_forward_model('pretrained/forward_400K.pyt')
voc_melgan = get_melgan_model() 
voc_wavernn = get_wavernn_model('pretrained/wave_575K.pyt')


# import torch
# from IPython.display import display, Audio
# torch.cuda.empty_cache()



# from pynvml import *
# nvmlInit()
# h = nvmlDeviceGetHandleByIndex(0)
# info = nvmlDeviceGetMemoryInfo(h)
# print(f'total    : {info.total/1000000000}')
# print(f'free     : {info.free/1000000000}')
# print(f'used     : {info.used/1000000000}')


# Synthesize with melgan (alpha=1.0)
input_text = 'How are you?'
wav = synthesize(input_text, tts_model, voc_melgan, alpha=1)
ipd.Audio(wav, rate=hp.sample_rate)



for text in SENTENCES:
    print(text)
    wav = synthesize(text, tts_model, voc_melgan, alpha=1)
    display(Audio(wav, rate=hp.sample_rate))
    torch.cuda.empty_cache()
    nvmlInit()
    h = nvmlDeviceGetHandleByIndex(0)
    info = nvmlDeviceGetMemoryInfo(h)
    print(f'total    : {info.total/1000000000}')
    print(f'free     : {info.free/1000000000}')
    print(f'used     : {info.used/1000000000}')



