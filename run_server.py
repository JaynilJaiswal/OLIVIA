from features.findInfo import FindInfoFinalData
from WebWhatsappWrapper.webwhatsapi import WhatsAPIDriver
from features.email import send_email
from features.music import getMusicDetails, getMusicFile_key
from utilities.featureWordExactMatch import exactMatchingWords
from features.location import getLocation
from features.weather import getWeather
from features.date import getDate
from features.time import getTime
from Models.generic_sound_classifier.audio_detect import *
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, Blueprint

import os
import requests
from scipy.io.wavfile import read, write
import io
import json
import time
import re

import numpy as np
import librosa
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from flask_login import LoginManager
from models.user import db, User, User_location, User_command_history, User_music, User_contacts_email, User_contacts_whatsapp
from flask_login import login_required, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# blueprint for auth routes in our app

from models.auth import auth as auth_blueprint
from findContactInfo import get_contact_email_info, get_contact_whatsapp_info
import shutil
from os import path
import spacy
nlp = spacy.load('en_core_web_sm')

db.create_all()

geolocator = Nominatim(user_agent="geoapiExercises")


STT_href = "http://127.0.0.1:5002"
TTS_href = "http://127.0.0.1:5001"
NLU_href = "http://127.0.0.1:5003"

audio_classifier = AudioClassifier()

base_inp_dir = "filesystem_for_data/Audio_input_files/"
base_out_dir = "filesystem_for_data/Audio_output_files/"
base_music_dir = "filesystem_for_data/Music_dir/"
base_gmail_dir = "filesystem_for_data/gmail_cred/"
base_whatsapp_cred_dir = "filesystem_for_data/Whatsapp_Cred/"

base_default_dir = "default_messages/"


app = Flask(__name__)

app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'

app.secret_key = '9OLWxND4o83j4K4iuopO'
data = []
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

app.register_blueprint(auth_blueprint)

run_server = Blueprint("run_server", __name__)
app.register_blueprint(run_server)

whatsapp_driver_dictionary = {}

# output_audio_ready = "no"
# corrector = DeepCorrect('Models/DeepCorrect_PunctuationModel/deeppunct_params_en', 'Models/DeepCorrect_PunctuationModel/deeppunct_checkpoint_google_news')
# FEATURE_LIST= ["time","date","location","weather","alarm reminder","schedule","music","find-information","message","email","call","features","translation"]

def select_feature(name, user_data, query):
    # global Music_filename
    # global music_thumbnail_url

    session['Music_filename'] = ""
    session['music_thumbnail_url'] = ""

    if name == "time":
        return [getTime(user_data["timezone"]), "time"]

    if name == 'date':
        return [getDate(user_data["timezone"]), "date"]

    if name == 'weather':
        if "city" in user_data['address']:
            return [getWeather(user_data['address']['city']), "weather"]
        elif "state_district" in user_data['address']:
            return [getWeather(user_data['address']['state_district']), "weather"]
        else:
            return ["Unable to find location to get weather related information.", "weather"]

    if name == 'location':
        return [getLocation(user_data['address']), "location"]

    if name == 'music':
        song_detail = get_associated_text(query, 'music')
        if song_detail == "":
            return ["Music not found, please give a better description.", "music"]

        [id_list, name_list, explicit_list, url] = getMusicDetails(song_detail)
        session['music_thumbnail_url'] = url[0]

        if id_list == 0:
            return ["Music not found, please give a better description.", "music"]

        if explicit_list[0] == "True":
            return ["Music contains explicit words.", "music"]

        if path.exists(base_music_dir + name_list[0] + ".m4a"):
            session['Music_filename'] = name_list[0]+".m4a"
            return ["Streaming "+name_list[0]+" now!", 'music']

        session['Music_filename'] = name_list[0]+".m4a"
        music_stream = getMusicFile_key(id_list[0], name_list[0])
        shutil.move(session['Music_filename'],
                    base_music_dir + session['Music_filename'])
        return [music_stream, "music"]

    if name == "email":
        contact_name = get_associated_text(query, 'email')
        if contact_name == "":
            return ["No match found for specified person or group in your contacts list. Would you like to add new person?", "email-contact-not-found"]
        [score, fullName, email] = get_contact_email_info(
            db, User_contacts_email, current_user.id, contact_name)

        if score == 0:
            return ["No match found for specified person or group in your contacts list. Would you like to add new person?", "email-contact-not-found"]
        elif score == -1:
            return ["Your contacts list is empty. Would you like to add a person?", "email-contact-not-found"]

        session["email-address"] = email
        session["email-fullname"] = fullName

        return ["Initiating email to "+fullName+". Please mention the subject of the email.", "email"]

    if name == "message":
        if path.exists(base_whatsapp_cred_dir+current_user.uname+"/profile.default/user.js") and path.exists(base_whatsapp_cred_dir+current_user.uname+"/profile.default/localStorage.json"):
            if current_user.uname not in whatsapp_driver_dictionary.keys():
                driver = WhatsAPIDriver(username=current_user.uname, profile=(
                    base_whatsapp_cred_dir+current_user.uname+"/profile.default"))

                counter = 0
                while not driver.is_logged_in():

                    counter += 1
                    if counter > 100000:
                        break

                if counter < 99999:
                    contact_name = get_associated_text(query, "message")
                    if contact_name == "":
                        return ["No match found for specified person or group in your contacts list. Please update your contacts for whatsapp.", "message-contact-not-found"]

                    # update_whatsapp_contact_list
                    db_contacts_available = list(
                        db.query(User_contacts_whatsapp).filter_by(user_base_id=current_user.id))
                    wh_contacts_available = driver.get_my_contacts()

                    db_contacts_tolist = [[el.contact_name, el.contact_id]
                                        for el in db_contacts_available]
                    wh_contacts_tolist = [[el.name, el.id]
                                        for el in wh_contacts_available]

                    if len(db_contacts_tolist) < len(wh_contacts_tolist):
                        not_available_contacts = [el for el in wh_contacts_tolist if not any(
                            [el[0] == k[0] for k in db_contacts_tolist])]
                        for el in not_available_contacts:
                            db.add(User_contacts_whatsapp(
                                user_base_id=current_user.id, contact_name=el[0], contact_id=el[1]))
                        db.commit()

                    # get contact info
                    [score, fullName, id] = get_contact_whatsapp_info(
                        db, User_contacts_whatsapp, current_user.id, contact_name)

                    if score == 0 or score == -1:
                        return ["No match found for specified person or group in your contacts list. Please update your phone contacts for whatsapp.", "message-contact-not-found"]

                    fullname = " ".join([re.sub(r'\W+', '', el)
                                        for el in fullName.split(" ")]).replace("  ", " ")

                    session['message-fullName'] = fullname
                    session['message-id'] = id
                    whatsapp_driver_dictionary[current_user.uname] = driver

                    return ["Logged into WhatsApp successfully. Please convey you message for " + fullname + ".", "message"]

                else:
                    driver = WhatsAPIDriver(username=current_user.uname)
                    session['QR_code_path'] = driver.get_qr()
                    session['qr_start_time'] = time.time()
                    whatsapp_driver_dictionary[current_user.uname] = driver
                    session['message-qr-code-query'] = query
                    return ["Please scan the QR code to log into Whatsapp web.", "message-scan-qr"]
            
            else:
                contact_name = get_associated_text(query, "message")
                if contact_name == "":
                    return ["No match found for specified person or group in your contacts list. Please update your contacts for whatsapp.", "message-contact-not-found"]

                # update_whatsapp_contact_list
                db_contacts_available = list(
                    db.query(User_contacts_whatsapp).filter_by(user_base_id=current_user.id))
                wh_contacts_available = whatsapp_driver_dictionary[current_user.uname].get_my_contacts()

                db_contacts_tolist = [[el.contact_name, el.contact_id]
                                    for el in db_contacts_available]
                wh_contacts_tolist = [[el.name, el.id]
                                    for el in wh_contacts_available]

                if len(db_contacts_tolist) < len(wh_contacts_tolist):
                    not_available_contacts = [el for el in wh_contacts_tolist if not any(
                        [el[0] == k[0] for k in db_contacts_tolist])]
                    for el in not_available_contacts:
                        db.add(User_contacts_whatsapp(
                            user_base_id=current_user.id, contact_name=el[0], contact_id=el[1]))
                    db.commit()

                # get contact info
                [score, fullName, id] = get_contact_whatsapp_info(
                    db, User_contacts_whatsapp, current_user.id, contact_name)

                if score == 0 or score == -1:
                    return ["No match found for specified person or group in your contacts list. Please update your phone contacts for whatsapp.", "message-contact-not-found"]

                fullname = " ".join([re.sub(r'\W+', '', el)
                                    for el in fullName.split(" ")]).replace("  ", " ")

                session['message-fullName'] = fullname
                session['message-id'] = id

                return ["Please convey you message for " + fullname + ".", "message"]

        else:
            driver = WhatsAPIDriver(username=current_user.uname)
            session['QR_code_path'] = driver.get_qr()
            session['qr_start_time'] = time.time()
            whatsapp_driver_dictionary[current_user.uname] = driver
            session['message-qr-code-query'] = query
            return ["Please scan the QR code to log into Whatsapp web.", "message-scan-qr"]

    if name == "alarm reminder":
        return ["Feature to be added soon.", "alarm reminder"]

    if name == "schedule":
        return ["Feature to be added soon.", "schedule"]

    if name == "find-information":
        context_detail = get_associated_text(query, 'find-information')
        
        [results,wiki_summary,wiki_image_list, wiki_url] = FindInfoFinalData(context_detail)

        if os.path.exists(base_out_dir + current_user.uname + "/search_urls.txt"):
                os.remove(base_out_dir + current_user.uname + "/search_urls.txt")

        with open(base_out_dir + current_user.uname + "/search_urls.txt","w") as f:
            f.write("#-#".join(results))

        if wiki_summary=="":
            return ["Displaying information for "+context_detail+" on your screen.", "find-information"]
        
        vocal_wiki_summary_output = ". ".join(wiki_summary.split(". ")[:2])
        return ["Sir, " + vocal_wiki_summary_output + "..... Other related articles and web links are displayed on your screen.", "find-information"]

    if name == "call":
        return ["Feature to be added soon.", "call"]

    if name == "features":
        return ["Feature to be added soon.", "features"]

    if name == "translation":
        return ["Feature to be added soon.", "translation"]


def get_associated_text(query, feature):
    if feature == 'music':
        if "play" in query:
            return query.split("play")[1]
        if "listen to" in query:
            return query.split("listen to")[1]
        if "listen" in query:
            return query.split("listen to")[1]
        if "lay" in query:
            return query.split("lay")[1]
        if "song" in query:
            return query.split("song")[0]
        if "music" in query:
            return query.split("music")[0]
        else:
            return query
    elif feature == 'email':
        # tagged = nlp(query)
        # return [e.text for e in text.ents if e.label_=="PERSON"]
        if "email" in query:
            return query.split("email")[1]
        if "mail" in query:
            return query.split("mail")[1]
        else:
            return ""
    elif feature == 'message':
        # tagged = nlp(query)
        # return [e.text for e in text.ents if e.label_=="PERSON"]
        if "message" in query:
            return query.split("message")[1]
        elif "whatsapp" in query:
            return query.split("whatsapp")[1]
        elif "chat with" in query:
            return query.split("chat with")[1]
        elif "ping" in query:
            return query.split("ping")[1]
        else:
            return ""
    elif feature == "find-information":
        if "information" in query:
            if "information on" in query: 
                return query.split("information on")[1]
            elif "information about" in query:
                return query.split("information about")[1]
            elif "information regarding" in query:
                return query.split("information regarding")[1]
            elif "information for" in query:
                return query.split("information for")[1]
            elif "information in regards to" in query:
                return query.split("information in regards to")[1]

        elif "info" in query:
            if "info on" in query: 
                return query.split("info on")[1]
            elif "info about" in query:
                return query.split("info about")[1]
            elif "info regarding" in query:
                return query.split("info regarding")[1]
            elif "info for" in query:
                return query.split("info for")[1]
            elif "info in regards to" in query:
                return query.split("info in regards to")[1]

        elif "detail" in query:
            if "detail on" in query: 
                return query.split("detail on")[1]
            elif "detail about" in query:
                return query.split("detail about")[1]
            elif "detail regarding" in query:
                return query.split("detail regarding")[1]
            elif "detail for" in query:
                return query.split("detail for")[1]
            elif "detail in regards to" in query:
                return query.split("detail in regards to")[1]

        elif "details" in query:
            if "details on" in query: 
                return query.split("details on")[1]
            elif "details about" in query:
                return query.split("details about")[1]
            elif "details regarding" in query:
                return query.split("details regarding")[1]
            elif "details for" in query:
                return query.split("details for")[1]
            elif "details in regards to" in query:
                return query.split("details in regards to")[1]
        
        else:
            return query
    return


def iterative_running_feature(filename, stage, user_data, feature_name):
    if feature_name == "message-scan-qr":
        if stage == 1:

            print("------------Saving web whatsapp profile--------------")

            whatsapp_driver_dictionary[current_user.uname]._profile_path = os.getcwd()+"/" +base_whatsapp_cred_dir + \
                current_user.uname+"/profile.default"
            whatsapp_driver_dictionary[current_user.uname].save_firefox_profile()

            ## getting contact info for the query
            contact_name = get_associated_text(
                session['message-qr-code-query'], "message")

            if contact_name == "":
                return ["No match found for specified person or group in your contacts list. Please update your contacts for whatsapp.", "message-contact-not-found"]

            # update_whatsapp_contact_list
            db_contacts_available = list(
                db.query(User_contacts_whatsapp).filter_by(user_base_id=current_user.id))
            wh_contacts_available = whatsapp_driver_dictionary[current_user.uname].get_my_contacts()

            db_contacts_tolist = [[el.contact_name, el.contact_id]
                                  for el in db_contacts_available]
            wh_contacts_tolist = [[el.name, el.id]
                                  for el in wh_contacts_available]

            if len(db_contacts_tolist) < len(wh_contacts_tolist):
                not_available_contacts = [el for el in wh_contacts_tolist if not any(
                    [el[0] == k[0] for k in db_contacts_tolist])]
                for el in not_available_contacts:
                    db.add(User_contacts_whatsapp(
                        user_base_id=current_user.id, contact_name=el[0], contact_id=el[1]))
                db.commit()

            # get contact info
            [score, fullName, id] = get_contact_whatsapp_info(
                db, User_contacts_whatsapp, current_user.id, contact_name)

            if score == 0 or score == -1:
                return ["No match found for specified person or group in your contacts list. Please update your phone contacts for whatsapp.", "message-contact-not-found"]

            fullname = " ".join([re.sub(r'\W+', '', el)
                                 for el in fullName.split(" ")]).replace("  ", " ")

            session['message-fullName'] = fullname
            session['message-id'] = id

            return ["Logged into WhatsApp successfully. Please convey you message for " + fullname + ".", "message"]

    if feature_name == "message":
        if stage == 2:
            payload = {'file': open(
                base_inp_dir + current_user.uname + "/" + filename, 'rb')}
            r = requests.post(STT_href, files=payload)
            print(r.text)
            input_str = json.loads(r.text)['text'][0]
            print(input_str)

            session["message-content"] = input_str

            db_com_str = "Content:" + input_str

            whatsapp_driver_dictionary[current_user.uname].send_message_to_id(
                session['message-id'], input_str)

            output = "Message sent successfully."

            new_user_ch = User_command_history(user_base_id=current_user.id, command_input_text=db_com_str, command_input_filepath=base_inp_dir +
                                               current_user.uname + "/" + filename, command_feature_selected="message-content", command_output_text=output)
            db.add(new_user_ch)
            db.commit()

            # TTS
            payload = {"input_str": output}
            r = requests.get(TTS_href, params=payload).json()
            bytes_wav = bytes()

            byte_io = io.BytesIO(bytes_wav)
            write(byte_io, r['rate'], np.array(r['data'], np.int16))

            output_wav = byte_io.read()

            if os.path.exists(base_out_dir + current_user.uname + "/" + 'result.wav'):
                os.remove(base_out_dir + current_user.uname +
                          "/" + 'result.wav')

            with open(base_out_dir + current_user.uname + "/" + 'result.wav', 'bx') as f:
                f.write(output_wav)

            # output_audio_ready = "yes"

            session['sel_feature'] = "message-sent"
            return "OK"

    if feature_name == "email":
        if stage == 1:

            #STT
            payload = {'file': open(
                base_inp_dir + current_user.uname + "/" + filename, 'rb')}
            r = requests.post(STT_href, files=payload)
            print(r.text)
            input_str = json.loads(r.text)['text'][0]
            print(input_str)

            session["email-subject"] = input_str

            db_com_str = "subject:" + input_str

            if os.path.exists(base_gmail_dir+current_user.uname+"/gmail_token.json"):
                output = "Please inform the message you want to convey to " + \
                    session["email-fullname"]+"."
            else:
                output = "Please inform the message you want to convey to " + \
                    session["email-fullname"] + \
                    ". Also login to Google account via registered email address with OLIVIA."

            new_user_ch = User_command_history(user_base_id=current_user.id, command_input_text=db_com_str, command_input_filepath=base_inp_dir +
                                               current_user.uname + "/" + filename, command_feature_selected="email-subject", command_output_text=output)
            db.add(new_user_ch)
            db.commit()

            # TTS
            payload = {"input_str": output}
            r = requests.get(TTS_href, params=payload).json()
            bytes_wav = bytes()

            byte_io = io.BytesIO(bytes_wav)
            write(byte_io, r['rate'], np.array(r['data'], np.int16))

            output_wav = byte_io.read()

            if os.path.exists(base_out_dir + current_user.uname + "/" + 'result.wav'):
                os.remove(
                    base_out_dir + current_user.uname + "/" + 'result.wav')

            with open(base_out_dir + current_user.uname + "/" + 'result.wav', 'bx') as f:
                f.write(output_wav)

            # output_audio_ready = "yes"

            session['sel_feature'] = "email-stage2"
            return "OK"

        elif stage == 2:

            #STT
            payload = {'file': open(
                base_inp_dir + current_user.uname + "/" + filename, 'rb')}
            r = requests.post(STT_href, files=payload)
            print(r.text)
            input_str = json.loads(r.text)['text'][0]
            print(input_str)

            session["email-body"] = input_str

            db_com_str = "Body:" + input_str

            os.chdir("filesystem_for_data/gmail_cred/"+current_user.uname)
            print("Input Params: "+session["email-address"]+" " + current_user.email +
                  " "+session["email-subject"]+" "+session["email-body"])
            output = send_email(session["email-address"], current_user.email,
                                session["email-subject"], session["email-body"])
            os.chdir('../../../')

            new_user_ch = User_command_history(user_base_id=current_user.id, command_input_text=db_com_str, command_input_filepath=base_inp_dir +
                                               current_user.uname + "/" + filename, command_feature_selected="email-body", command_output_text=output)
            db.add(new_user_ch)
            db.commit()

            # TTS
            payload = {"input_str": output}
            r = requests.get(TTS_href, params=payload).json()
            bytes_wav = bytes()

            byte_io = io.BytesIO(bytes_wav)
            write(byte_io, r['rate'], np.array(r['data'], np.int16))

            output_wav = byte_io.read()

            if os.path.exists(base_out_dir + current_user.uname + "/" + 'result.wav'):
                os.remove(base_out_dir + current_user.uname +
                          "/" + 'result.wav')

            with open(base_out_dir + current_user.uname + "/" + 'result.wav', 'bx') as f:
                f.write(output_wav)

            # output_audio_ready = "yes"

            session['sel_feature'] = "email-stage3"
            return "OK"


def backend_pipeline(filename, user_data):

    #STT
    payload = {'file': open(
        base_inp_dir + current_user.uname + "/" + filename, 'rb')}
    r = requests.post(STT_href, files=payload)
    print(r.text)
    input_str = json.loads(r.text)['text'][0]
    print(input_str)

    db_com_str = input_str

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

    input_str = text
    # NEED to figure out punctuation issue.
    # input_str = corrector.correct(text)[0]['sequence']
    print("Preprocessed text: " + input_str)

    #NLU
    ## Checking for exact match

    [token, feature_l] = exactMatchingWords(text)
    if token == "single feature selected":
        print("====================================================================")
        print("====================================================================")
        print("======================Result As per Tagging=========================")
        print(str(feature_l))
        print("====================================================================")
        print("\n")

        input_str = [select_feature(feature_l[0], user_data, text)]
        print(input_str)
        
    elif token == "multiple features selected":
        print("====================================================================")
        print("====================================================================")
        print("======================Result As per Tagging=========================")
        print(str(feature_l))
        print("====================================================================")
        print("\n")

        input_str = [select_feature(feature_l[i], user_data, text)
                     for i in range(len(feature_l))]

    elif token == "no feature tag found":
        r = requests.get(NLU_href, json={"sentence": text}).json()

        print("Most related feature : "+str(r['Most related feature'][0][0]))
        print("\n")
        print("====================================================================")
        print("======================Result As per NLP-Shell=======================")
        print(str(r['Most related feature']))
        print("====================================================================")
        print("\n")

        if float(r['Most related feature'][0][1]) > 0.5:
            input_str = [select_feature("find-information", user_data, text)]

        else:
            input_str = [select_feature( r['Most related feature'][0][0], user_data, text)]


    new_user_ch = User_command_history(user_base_id=current_user.id, command_input_text=db_com_str, command_input_filepath=base_inp_dir +
                                       current_user.uname + "/" + filename, command_feature_selected=input_str[0][1], command_output_text=input_str[0][0])
    db.add(new_user_ch)
    db.commit()

    #TTS
    final_input = ""
    for i in range(len(input_str)):
        final_input = final_input + "..." + input_str[i][0]
    payload = {"input_str": final_input}
    r = requests.get(TTS_href, params=payload).json()
    bytes_wav = bytes()

    byte_io = io.BytesIO(bytes_wav)
    write(byte_io, r['rate'], np.array(r['data'], np.int16))

    output_wav = byte_io.read()

    if os.path.exists(base_out_dir + current_user.uname + "/" + 'result.wav'):
        os.remove(base_out_dir + current_user.uname + "/" + 'result.wav')

    with open(base_out_dir + current_user.uname + "/" + 'result.wav', 'bx') as f:
        f.write(output_wav)

    session['sel_feature'] = ", ".join(
        [input_str[i][1] for i in range(len(input_str))])

    return "OK"

    # code to validate and add user to database goes here
    # return redirect(url_for('auth.login'))


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return db.query(User).get(int(user_id))


@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        if current_user.is_authenticated:
            session['add_contacts_post_requests'] = False
            return redirect(url_for('home'))
        else:
            return render_template('index.html')


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'GET':
        session['sel_feature'] = ""
        session['Music_filename'] = ""
        session['music_thumbnail_url'] = ""
        session['command_in_progress'] = False

        if(session['add_contacts_post_requests'] != True):
            return render_template('home.html', fname=current_user.fname, getWelcome_msg="true")
        else:
            session['add_contacts_post_requests'] = False
            return render_template('home.html', fname=current_user.fname, getWelcome_msg="false")

    if request.method == "POST":
        user_location = json.loads(request.form['data'])

        tf = TimezoneFinder()
        user_timezone = tf.timezone_at(
            lng=user_location['long'], lat=user_location['lat'])

        user_address = geolocator.reverse(
            str(user_location['lat'])+','+str(user_location['long'])).raw['address']

        if 'city' in user_address and 'state_district' in user_address:
            new_user_location = User_location(user_base_id=current_user.id, latitude=user_location["lat"], longitude=user_location["long"], timezone=user_timezone, city=user_address[
                                              'city'], state_district=user_address['state_district'], state=user_address['state'], postcode=user_address['postcode'], country=user_address['country'], country_code=user_address['country_code'])
        elif 'city' not in user_address and 'state_district' in user_address:
            new_user_location = User_location(user_base_id=current_user.id, latitude=user_location["lat"], longitude=user_location["long"], timezone=user_timezone, city="Not found", state_district=user_address[
                                              'state_district'], state=user_address['state'], postcode=user_address['postcode'], country=user_address['country'], country_code=user_address['country_code'])
        elif 'city' in user_address and 'state_district' not in user_address:
            new_user_location = User_location(user_base_id=current_user.id, latitude=user_location["lat"], longitude=user_location["long"], timezone=user_timezone, city=user_address[
                                              'city'], state_district="Not found", state=user_address['state'], postcode=user_address['postcode'], country=user_address['country'], country_code=user_address['country_code'])
        else:
            new_user_location = User_location(user_base_id=current_user.id, latitude=user_location["lat"], longitude=user_location["long"], timezone=user_timezone, city="Not found",
                                              state_district="Not found", state=user_address['state'], postcode=user_address['postcode'], country=user_address['country'], country_code=user_address['country_code'])

        session['user_data'] = {'location': user_location,
                                'timezone': user_timezone, 'address': user_address}
        print(session['user_data'])

        db.add(new_user_location)
        db.commit()

        db.session.commit()
        return "saved"


@app.route('/process', methods=['GET', 'POST'])
def process():
    if request.method == 'POST':
        if request.form["contains_audio"] == "true":
            filename = request.files['audio_data'].filename
            audio, sr = librosa.load(request.files['audio_data'])
            print(request.form['stage'])
            if request.form['stage'] == '0':
                labels = audio_classifier.detect(audio)
                print(len(audio), labels)
                if "Finger snapping" in labels:
                    session['command_in_progress'] = True
                    print(session['command_in_progress'])
                    return {"continue": "YES", "listen": "YES"}
                else:
                    if session['command_in_progress']:
                        print(session['command_in_progress'])
                        session['command_in_progress'] = False
                        librosa.output.write_wav(
                            base_inp_dir + current_user.uname + "/" + filename, audio, sr)
                        # try:
                        backend_pipeline(filename, session['user_data'])
                        return {"continue": "NO", "listen": "NO", "error": "NO"}
                        # except:
                        #     session['command_in_progress'] = False
                        #     print("Exception in backend_pipeline")
                        #     return {"continue": "YES", "listen": "NO", "error": "YES"}

                        # return {"continue":"NO","listen":"NO"}
                    else:
                        print(session['command_in_progress'])
                        session['command_in_progress'] = False
                        return {"continue": "YES", "listen": "NO"}
            else:
                print(request.form['stage'])
                librosa.output.write_wav(
                    base_inp_dir + current_user.uname + "/" + filename, audio, sr)
                iterative_running_feature(filename, ord(
                    request.form['stage'])-ord('0'), session['user_data'], request.form['feature'])
                return {"continue": "NO"}
        else:
            print(request.form['stage'])
            iterative_running_feature("", ord(
                request.form['stage'])-ord('0'), session['user_data'], request.form['feature'])
            return {"continue": "NO"}


@app.route("/set_command", methods=['POST'])
def set_command():
    session['command_in_progress'] = True
    return "OK"


@app.route('/fetch_output_audio', methods=['POST', 'GET'])
def fetch_output_audio():
    if request.method == "POST":
        return send_file(base_out_dir + current_user.uname + "/" + 'result.wav', mimetype="audio/wav", as_attachment=True, attachment_filename='result.wav')

    if request.method == "GET":
        if os.path.exists(base_out_dir + current_user.uname + "/" + 'result.wav'):
            os.remove(base_out_dir + current_user.uname +
                      "/" + 'result.wav')
        return "output file removed"


@app.route('/get_qr_code', methods=['GET', 'POST'])
def get_qr_code():
    print(time.time() - session['qr_start_time'])
    # if time.time() - session['qr_start_time'] > 19.99:
    #     session['qr_start_time'] = time.time()
    session['QR_code_path'] = whatsapp_driver_dictionary[current_user.uname].get_qr()
    print("new QR code")
    return send_file(session['QR_code_path'], mimetype="image/png", as_attachment=True, attachment_filename="qr_code_"+current_user.uname+".png")


@app.route('/whatsapp_logged_in', methods=['GET'])
def whatsapp_logged_in():
    if request.method == 'GET':
        if whatsapp_driver_dictionary[current_user.uname].is_logged_in():
            return "1"
        return "0"


@app.route('/add_contacts', methods=['POST'])
def add_contacts():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        s_email = request.form['second_email']

        new_contact = User_contacts_email(user_base_id=current_user.id, contact_fname=fname,
                                          contact_lname=lname, contact_email=email, contact_second_email=s_email)
        db.add(new_contact)
        db.commit()

        session['add_contacts_post_requests'] = True

        return redirect(url_for('home'))


@app.route("/getfeature_name", methods=['GET'])
def getfeature_name():
    return session['sel_feature']


@app.route("/fetch_music_audio", methods=['GET', 'POST'])
def fetch_music_audio():
    # global Music_filename
    if request.method == "POST" and session['Music_filename'] != "":
        return send_file(base_music_dir + session['Music_filename'], mimetype="audio/m4a", as_attachment=True, attachment_filename=session['Music_filename'])


@app.route("/getWelcomeMessage", methods=['GET', 'POST'])
def getWelcomeMessage():
    if request.method == "POST":
        file_path = "default_messages/welcome_message_" + \
            str(current_user.gender)+".wav"
        return send_file(file_path, mimetype="audio/wav", as_attachment=True)


@app.route("/getMusicDetails_toShow", methods=["GET"])
def getMusicDetails_toShow():
    if request.method == "GET":
        return session['Music_filename']+"###--###"+session['music_thumbnail_url']

@app.route("/getFindInfoDetails_toShow",methods=["GET"])
def getFindInfoDetails_toShow():
    if request.method == "GET":
        with open(base_out_dir + current_user.uname + "/search_urls.txt","r") as f:
            results = f.read()
        results = results.strip()

        return results

if __name__ == "__main__":
    app.run(debug=True)
