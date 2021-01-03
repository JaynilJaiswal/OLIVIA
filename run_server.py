from flask import Flask,render_template,request,redirect,url_for,session,jsonify,send_file
import os
import requests
from scipy.io.wavfile import read,write
import io
import json
import numpy as np
import time

STT_href = "http://470e143e4819.ngrok.io/"
TTS_href = "http://ddfc0d5a8c7c.ngrok.io/"
NLU_href = "http://e6422c082e4e.ngrok.io/"

base_inp_dir = "Audio_input_files/"
base_out_dir = "Audio_output_files/"

app = Flask(__name__)
app.secret_key = 'random'
@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='GET':
        return render_template('index.html')

@app.route('/process',methods=['GET','POST'])
def process():
    if request.method=='POST':
        
        f  = request.files['audio_data']
        with open(base_inp_dir + f.filename,'wb') as audio:
            f.save(audio)
        
        #STT
        payload={'file':open(base_inp_dir + f.filename,'rb')}
        r = requests.post(STT_href,files=payload)

        #NLU        
        input_str=json.loads(r.text)['text'][0]
        print (input_str+"?")
        r = requests.get(NLU_href,json={"sentence":input_str}).json()
        print("Most related feature : "+str(r['Most related feature']))

        #TTS
        r = requests.get(TTS_href, params={"input_str":input_str}).json()
        bytes_wav = bytes()
        byte_io = io.BytesIO(bytes_wav)
        write(byte_io, r['rate'], np.array(r['data'],np.int16))
        output_wav = byte_io.read() 

        with open(base_out_dir + 'result.wav','wb') as f:
            f.write(output_wav)
        
        return "OK"

@app.route('/check_audio_available', methods=['GET'])
def check_audio_available():
    if request.method=="GET":
        if os.path.exists(base_out_dir + '/result.wav'):
            # payload={'play':1 , 'file': open('Audio_output_files/result.wav','rb')}
            return "yes"
        else:
            return "no"

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