from flask import Flask,render_template,request,redirect,url_for,session,jsonify,send_file
import os
import requests
from scipy.io.wavfile import read,write
import io
import json
import numpy as np
import time

STT_href = "http://0b14607194e2.ngrok.io/"
TTS_href = "http://4331bdaf2a7f.ngrok.io/"
NLU_href = "http://b04a71104cfb.ngrok.io/"
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
        with open(f.filename,'wb') as audio:
            f.save(audio)
        payload={'file':open(f.filename,'rb')}
        r = requests.post(STT_href,files=payload)
        input_str=json.loads(r.text)['text'][0]
        print (input_str)
        r = requests.get(NLU_href,json={"sentence":input_str}).json()
        print("Most related feature : "+r['Most related feature'][0][0])
        r = requests.get(TTS_href, params={"input_str":input_str}).json()
        bytes_wav = bytes()
        byte_io = io.BytesIO(bytes_wav)
        write(byte_io, r['rate'], np.array(r['data'],np.int16))
        print(r['rate'])
        output_wav = byte_io.read() 
        # print(output_wav)
        with open('Audio_output_files/result.wav','wb') as f:
            f.write(output_wav)
        # time.sleep(2)
        # if os.path.exists('static/Audio_output_files/result.wav'):
        #     os.remove('static/Audio_output_files/result.wav')
        return "OK"
@app.route('/check', methods=['GET','POST'])
def check():
    if request.method=="POST":
        if os.path.exists('Audio_output_files/result.wav'):
            # payload={'play':1 , 'file': open('Audio_output_files/result.wav','rb')}
            print("yes")
            return send_file('Audio_output_files/result.wav',mimetype="audio/x-wav",as_attachment=True,attachment_filename='result.wav')
        else:
            return "no"
if __name__ == "__main__":
    app.run(debug=True)