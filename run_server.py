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
from utilities.featureWordExactMatch import exactMatchingWords
from features.music import getMusicDetails, check_if_already_available, getMusicFile_key

STT_href = "http://34ae48447ded.ngrok.io/"
TTS_href = "http://17cdc6ac68a9.ngrok.io/"
NLU_href = "http://9e042c13ad5c.ngrok.io/"

base_inp_dir = "Audio_input_files/"
base_out_dir = "Audio_output_files/"
base_default_dir = "default_messages/"
base_music_dir = "Music_dir/"

Music_filename = ""

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
sel_feature = ""
music_thumbnail_url = ""
# corrector = DeepCorrect('Models/DeepCorrect_PunctuationModel/deeppunct_params_en', 'Models/DeepCorrect_PunctuationModel/deeppunct_checkpoint_google_news')
# FEATURE_LIST= ["time","date","location","weather","alarm reminder","schedule","music","find information","message","email","call","features","translation"]

def select_feature(name,user_data,query):
    global Music_filename
    global music_thumbnail_url

    if name=="time":
        return [getTime(user_data["timezone"]),"time"]

    if name=='date':
        return [getDate(user_data["timezone"]),"date"]

    if name=='weather':
        if "city" in user_data['address']:
            return [getWeather(user_data['address']['city']),"weather"]
        elif "state_district" in user_data['address']:
            return [getWeather(user_data['address']['state_district']),"weather"]
        else:
            return ["Unable to find location to get weather related information.","weather"]

    if name=='location':
        return [getLocation(user_data['address']),"location"]

    if name == 'music':
        song_detail = get_associated_text(query)

        [id_list,name_list,explicit_list,url] = getMusicDetails(song_detail)
        music_thumbnail_url = url

        if id_list == 0: 
            return ["Music not found, please give a better description.","music"]
        
        if explicit_list[0] == "True":
            return ["Music contains explicit words.","music"]
            
        if check_if_already_available(name_list[0]):
            return ["Streaming "+name_list[0]+" now!",'music']   

        Music_filename = name_list[0]+".m4a" 

        return [getMusicFile_key(id_list[0],name_list[0]),"music"]

    if name =="alarm reminder":
        return ["Feature to be added soon.","alarm reminder"]

    if name =="schedule":
        return ["Feature to be added soon.","schedule"]

    if name =="find information":
        return ["Feature to be added soon.","find information"]

    if name =="message":
        return ["Feature to be added soon.","message"]

    if name =="email":
        return ["Feature to be added soon.","email"]

    if name =="call":
        return ["Feature to be added soon.","call"]

    if name =="features":
        return ["Feature to be added soon.","features"]

    if name =="translation":
        return ["Feature to be added soon.","translation"]


def get_associated_text(query):
    if "play" in query:
        return query.split("play")[1]
    if "listen to" in query:
        return query.split("listen to")[1]
    if "listen" in query:
        return query.split("listen to")[1]
    if "lay" in query:
        return query.split("lay")[1]
    else:
        return ""


def backend_pipeline(request,user_data):
    
    global output_audio_ready
    global sel_feature
    
    output_audio_ready = "no"

    f  = request.files['audio_data']
    with open(base_inp_dir + f.filename,'wb') as audio:
        f.save(audio)
        
    #STT
    payload={'file':open(base_inp_dir + f.filename,'rb')}
    r = requests.post(STT_href,files=payload)
    print(r)
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
    if 'olivi' in text:
        text = text.split('olivi')[1].strip()
    if 'olivie' in text:
        text = text.split('olivie')[1].strip()

    input_str = text + "?"
    # NEED to figure out punctuation issue.
    # input_str = corrector.correct(text)[0]['sequence']
    print("Preprocessed text: " + input_str)

    #NLU
    ## Checking for exact match

    [token,feature_l] = exactMatchingWords(text)
    if token == "single feature selected":
        print("====================================================================")
        print("====================================================================")
        print("======================Result As per Tagging=========================")
        print(str(feature_l))
        print("====================================================================")
        print("\n")
        input_str = [select_feature(feature_l[0],user_data,text)]

    elif token == "multiple features selected":
        # r = requests.get(NLU_href,json={"sentence":text}).json()

        # print("Most related feature : "+str(r['Most related feature'][0][0]))
        # print("\n")
        print("====================================================================")
        print("====================================================================")
        print("======================Result As per Tagging=========================")
        print(str(feature_l))
        print("====================================================================")
        print("\n")
        
        input_str = [select_feature(feature_l[i],user_data,text) for i in range(len(feature_l))]
        
    elif token == "no feature tag found":
        r = requests.get(NLU_href,json={"sentence":text}).json()

        print("Most related feature : "+str(r['Most related feature'][0][0]))
        print("\n")
        print("====================================================================")
        print("======================Result As per NLP-Shell=======================")
        print(str(r['Most related feature']))
        print("====================================================================")
        print("\n")
        
        input_str = [select_feature(r['Most related feature'][0][0],user_data,text)]

    #TTS        
    final_input = ""
    for i in range(len(input_str)):
        final_input = final_input + input_str[i][0]
    payload={"input_str": final_input}
    r = requests.get(TTS_href, params=payload).json()

    r = requests.get(TTS_href, params={"input_str":input_str[0]}).json()
    bytes_wav = bytes()

    byte_io = io.BytesIO(bytes_wav)
    write(byte_io, r['rate'], np.array(r['data'],np.int16))
    
    output_wav = byte_io.read() 
    
    if os.path.exists(base_out_dir + 'result.wav'):
        os.remove(base_out_dir + 'result.wav')
        
    with open(base_out_dir + 'result.wav','bx') as f:
        f.write(output_wav)

    output_audio_ready = "yes"

    sel_feature = ", ".join([input_str[i][1] for i in range(len(input_str))])

    return "OK"

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
        return backend_pipeline(request,session['user_data'])

@app.route('/check_audio_available', methods=['GET'])
def check_audio_available():
    if request.method=="GET":
            return output_audio_ready

# @app.route('/too_long_time_to_process',methods=['POST'])
# def too_long_time_to_process():
#     global output_audio_ready
#     output_audio_ready = "yes"
#     return send_file(base_default_dir + 'timeout_default_for_'+current_user.gender+'.wav',mimetype="audio/wav",as_attachment=True,attachment_filename='timeout_default_for_'+current_user.gender+'.wav')

@app.route('/fetch_output_audio', methods=['POST','GET'])
def fetch_output_audio():
        if request.method=="POST":
            return send_file(base_out_dir + 'result.wav',mimetype="audio/wav",as_attachment=True,attachment_filename='result.wav')

        if request.method=="GET":
            if os.path.exists(base_out_dir + 'result.wav'):
                os.remove(base_out_dir + 'result.wav')
            return "output file removed"

@app.route("/getfeature_name",methods = ['GET'])
def getfeature_name():
    return sel_feature

@app.route("/fetch_music_audio",methods = ['GET','POST'])
def fetch_music_audio():
    global Music_filename
    if request.method=="POST" and Music_filename!="":
        return send_file(Music_filename,mimetype="audio/m4a",as_attachment=True,attachment_filename=Music_filename)

@app.route("/getWelcomeMessage",methods = ['GET','POST'])
def getWelcomeMessage():
    if request.method=="POST":
        file_path = "default_messages/welcome_message_"+str(current_user.gender)+".wav"
        return  send_file(file_path,mimetype="audio/wav",as_attachment=True)

@app.route("/getMusicDetails_toShow",methods=["GET"])
def getMusicDetails_toShow():
    if request.method=="GET":
        return Music_filename+"###--###"+music_thumbnail_url

if __name__ == "__main__":
    app.run(debug=True)

