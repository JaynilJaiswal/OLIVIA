from flask import Flask,render_template,request,redirect,url_for,session,jsonify,send_file
# from deepcorrect import DeepCorrect
import os
import requests
from scipy.io.wavfile import read,write
import io
import json
from pydub import AudioSegment
import numpy as np
import time

STT_href = "http://ecf1af5381ed.ngrok.io/"
TTS_href = "http://05eebc8e95b6.ngrok.io/"
NLU_href = "http://c9638bd7a68b.ngrok.io/"
preprocess_href = "http://127.0.0.1:5040/"

base_inp_dir = "Audio_input_files/"
base_out_dir = "Audio_output_files/"

app = Flask(__name__)
app.secret_key = 'random'

output_audio_ready = "no"

# corrector = DeepCorrect('Models/DeepCorrect_PunctuationModel/deeppunct_params_en', 'Models/DeepCorrect_PunctuationModel/deeppunct_checkpoint_google_news')

def backend_pipeline(request):
    
    global output_audio_ready
    
    output_audio_ready = "no"

    f  = request.files['audio_data']
    with open(base_inp_dir + f.filename,'wb') as audio:
        f.save(audio)
        
    #STT
    payload={'file':open(base_inp_dir + f.filename,'rb')}
    r = requests.post(STT_href,files=payload)
    input_str=json.loads(r.text)['text'][0]
    print (input_str)

    #preprocess   
    text = input_str    
    if 'olivia' in text:
        text = text.split('olivia')[1].strip()
    if 'alivia' in text:
        text = text.split('olivia')[1].strip()
    if 'olvia' in text:
        text = text.split('olvia')[1].strip()
    if 'oliva' in text:
        text = text.split('oliva')[1].strip()
    if 'holivia' in text:
        text = text.split('holivia')[1].strip()

    input_str = text + "?"
    # NEED to figure out punctuation issue.
    # input_str = corrector.correct(text)[0]['sequence']
    print("Preprocessed text: " + input_str)

    #NLU
    r = requests.get(NLU_href,json={"sentence":text}).json()
    print("Most related feature : "+str(r['Most related feature']))

    #TTS        
    payload={"input_str": input_str }
    r = requests.get(TTS_href, params=payload).json()

    r = requests.get(TTS_href, params={"input_str":input_str}).json()
    bytes_wav = bytes()

    byte_io = io.BytesIO(bytes_wav)
    write(byte_io, r['rate'], np.array(r['data'],np.int16))
    
    output_wav = byte_io.read() 
    
    if os.path.exists(base_out_dir + 'result.wav'):
        os.remove(base_out_dir + 'result.wav')
        
    with open(base_out_dir + 'result.wav','bx') as f:
        f.write(output_wav)

    output_audio_ready = "yes"


@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='GET':
        return render_template('index.html')

@app.route('/process',methods=['GET','POST'])
def process():
    if request.method=='POST':

        backend_pipeline(request)
        
        return "OK"

@app.route('/check_audio_available', methods=['GET'])
def check_audio_available():
    if request.method=="GET":
            return output_audio_ready

@app.route('/fetch_output_audio', methods=['POST','GET'])
def fetch_output_audio():
        if request.method=="POST":
            return send_file(base_out_dir + 'result.wav',mimetype="audio/wav",as_attachment=True,attachment_filename='result.wav')

        if request.method=="GET":
            if os.path.exists(base_out_dir + 'result.wav'):
                os.remove(base_out_dir + 'result.wav')
            return "output file removed"


if __name__ == "__main__":
    app.run(debug=True)