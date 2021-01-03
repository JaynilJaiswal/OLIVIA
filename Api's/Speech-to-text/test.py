import requests
from scipy.io.wavfile import read,write
import io
import json
import numpy as np

base="http://0b14607194e2.ngrok.io/"
payload={'file':open('test.wav','rb')}

r = requests.post(url=base,files=payload)
print(json.loads(r.text)['text'][0])
# print(r.text)