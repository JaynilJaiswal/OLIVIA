from flask import Flask,render_template,request,redirect,url_for,session,jsonify,send_file
import os
import json
app = Flask(__name__)
app.secret_key = 'random'
@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='GET':
        # global play
        session['play']=0
        print(session['play'])
        return render_template('index.html',play=session['play'])

@app.route('/process',methods=['GET','POST'])
def process():
    if request.method=='GET':
        if os.path.exists('static/Audio_output_files/result.wav'):
            # payload={'play':1 , 'file': open('static/Audio_output_files/result.wav','rb')}
            return send_file('static/Audio_output_files/result.wav')
        else:
            return "no"
    if request.method=='POST':
        f  = request.files['audio_data']
        with open(f.filename,'wb') as audio:
            f.save(audio)
        return "OK"
if __name__ == "__main__":
    app.run(debug=True)