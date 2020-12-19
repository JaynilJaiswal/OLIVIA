import requests
from scipy.io.wavfile import read,write
import io
from pydub import AudioSegment
import numpy as np

base="http://127.0.0.1:5000/"
payload={"input_str":"How are you?"}
r = requests.get(base, params=payload).json()
print(r['rate'])
# open('result.wav','wb').write(r.content)
bytes_wav = bytes()

byte_io = io.BytesIO(bytes_wav)
write(byte_io, r['rate'], np.array(r['data'],np.int16))
print(bytes_wav)
output_wav = byte_io.read() 
# print(output_wav)
with open('result.wav','bx') as f:
    f.write(output_wav)