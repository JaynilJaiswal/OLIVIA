import io,librosa,wave,struct
def write_header(_bytes, _nchannels, _sampwidth, _framerate):
    WAVE_FORMAT_PCM = 0x0001
    initlength = len(_bytes)
    bytes_to_add = b'RIFF'
    
    _nframes = initlength // (_nchannels * _sampwidth)
    _datalength = _nframes * _nchannels * _sampwidth

    bytes_to_add += struct.pack('<L4s4sLHHLLHH4s',
        36 + _datalength, b'WAVE', b'fmt ', 16,
        WAVE_FORMAT_PCM, _nchannels, _framerate,
        _nchannels * _framerate * _sampwidth,
        _nchannels * _sampwidth,
        _sampwidth * 8, b'data')

    bytes_to_add += struct.pack('<L', _datalength)

    return bytes_to_add + _bytes
f= wave.open('result.wav','rb')
params = list(f.getparams())
frames = f.readframes(10000000000)
filebytes = write_header(frames,params[0],params[1],params[2])
data,sr = librosa.load(io.BytesIO(filebytes))
print (sr,len(data))