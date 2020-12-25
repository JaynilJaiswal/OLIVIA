import requests
from scipy.io.wavfile import read,write
import io
import json
import numpy as np

base="http://127.0.0.1:5000/"
payload={'file':open('test.wav','rb')}

r = requests.post(base, files=payload)
print(json.loads(r.text)['text'][0])