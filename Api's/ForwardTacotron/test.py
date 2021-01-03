import requests
from scipy.io.wavfile import read,write
import io
from pydub import AudioSegment
import numpy as np

base="http://4331bdaf2a7f.ngrok.io/"
payload={"input_str":"what's the time right now?"}
r = requests.get(base, params=payload).json()
print(r['rate'])
# open('result.wav','wb').write(r.content)
bytes_wav = bytes()

byte_io = io.BytesIO(bytes_wav)
write(byte_io, r['rate'], np.array(r['data'],np.int16))
print(bytes_wav)
output_wav = byte_io.read() 
# print(output_wav)
with open('result.wav','wb') as f:
    f.write(output_wav)