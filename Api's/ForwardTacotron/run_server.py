from flask import Flask, request
from flask_restful import Api,Resource,reqparse
from scipy.io.wavfile import read,write
import io
from notebook_utils.synthesize import (
    get_forward_model, get_melgan_model, get_wavernn_model, synthesize, init_hparams)
from utils import hparams as hp

app= Flask(__name__)
api=Api(app)

init_hparams('notebook_utils/pretrained_hparams.py')
tts_model = get_forward_model('pretrained/forward_400K.pyt')
voc_melgan = get_melgan_model() 
# voc_wavernn = get_wavernn_model('pretrained/wave_575K.pyt')

class hello(Resource):
    def get(self):
        print(request.args['input_str'])
        input_text=request.args['input_str']
        output_wav=synthesize(input_text, tts_model, voc_melgan, alpha=1)
        # with open('test.wav','rb') as wavfile:
        #     output_wav=wavfile.read()
        # rate, data = read(io.BytesIO(output_wav))
        # print(rate)
        # print(data)
        return {"result": request.args['input_str'],"rate": hp.sample_rate, "data": output_wav.tolist()}

api.add_resource(hello,"/")

if __name__ == "__main__":
    app.run(debug=True)
