from flask import Flask,render_template,request,redirect,url_for,session,jsonify,send_file, Blueprint
# from deepcorrect import DeepCorrect
import os
import requests
from scipy.io.wavfile import read,write
import io
import json
from pydub import AudioSegment
import numpy as np
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from flask_login import LoginManager
from models.user import db, User
from flask_login import login_required, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
# blueprint for auth routes in our app
from models.auth import auth as auth_blueprint

db.create_all()

geolocator = Nominatim(user_agent="geoapiExercises") 

from features.time import getTime
from features.date import getDate
from features.weather import getWeather
from features.location import getLocation

STT_href = "http://3d80329a052b.ngrok.io/"
TTS_href = "http://d958464f99ad.ngrok.io/"
NLU_href = "http://eb1f4abab983.ngrok.io/"

base_inp_dir = "Audio_input_files/"
base_out_dir = "Audio_output_files/"

app = Flask(__name__)

app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'

app.secret_key = '9OLWxND4o83j4K4iuopO'

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

app.register_blueprint(auth_blueprint)

run_server = Blueprint("run_server",__name__)
app.register_blueprint(run_server)


output_audio_ready = "no"
# corrector = DeepCorrect('Models/DeepCorrect_PunctuationModel/deeppunct_params_en', 'Models/DeepCorrect_PunctuationModel/deeppunct_checkpoint_google_news')
# FEATURE_LIST= ["time","date","location","weather","alarm reminder","schedule","music","find information","message","email","call","features","translation"]

def select_feature(name,user_data):
    if name=="time":
        return getTime(user_data["timezone"])
    if name=='date':
        return getDate(user_data["timezone"])
    if name=='weather':
        return getWeather(user_data['address']['city'])
    if name=='location':
        return getLocation(user_data['address'])


def backend_pipeline(request,user_data):
    
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
    print("Most related feature : "+str(r['Most related feature'][0][0]))
    print("\n")
    print("====================================================================")
    print("=========================Complete result============================")
    print(str(r['Most related feature']))
    print("====================================================================")
    print("====================================================================")
    print("\n")
    
    #Feature
    input_str = select_feature(r['Most related feature'][0][0],user_data)
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

    # code to validate and add user to database goes here
    # return redirect(url_for('auth.login'))

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return db.query(User).get(int(user_id))

@app.route('/',methods=['GET'])
def index():
    if request.method=='GET':
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        else:
            return render_template('index.html')
         

@app.route('/home',methods=['GET','POST'])
@login_required
def home():
    if request.method=='GET':
        return render_template('home.html',fname=current_user.fname)
    if request.method=="POST":
        user_location =json.loads(request.form['data'])
        current_user.latitude = user_location["lat"]
        current_user.longitude = user_location["long"]

        tf = TimezoneFinder()
        user_timezone = tf.timezone_at(lng=user_location['long'],lat=user_location['lat'])
        current_user.timezone = user_timezone

        user_address = geolocator.reverse(str(user_location['lat'])+','+str(user_location['long'])).raw['address']
        current_user.address = user_address

        session['user_data']= {'location':user_location,'timezone':user_timezone,'address':user_address}
        print (session['user_data'])
        
        db.session.commit()
        return "saved"

@app.route('/process',methods=['GET','POST'])
def process():
    if request.method=='POST':
        backend_pipeline(request,session['user_data'])
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
