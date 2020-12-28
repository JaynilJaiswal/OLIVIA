from flask import Flask, request, jsonify
from flask_restful import Api,Resource,reqparse
from sentence_transformers import SentenceTransformer
import scipy
import numpy as np

app= Flask(__name__)
api=Api(app)
model = SentenceTransformer('xlm-r-100langs-bert-base-nli-stsb-mean-tokens')
# xlm-r-100langs-bert-base-nli-stsb-mean-tokens
# bert-base-nli-mean-tokens

feature_db = {
		"time":['time','clock','how much time is the clock showing','what time zone are you following','what is the time right now',"what's the time","What time is it","tell me the time",'tell me time in london','tell me time in usa','tell me time in sydney right now','what is time in australia right now','right now','at this moment'],

		"date":["date","occasion","day","month","year","todays's date","what day is it today","what is the occasion today","is there something special today","why is there a public holiday tomorrow","working day","weekends"],

		"location":["location","where am i","whats my location","where am i right now exact address","where am i ip","where am i address","where am i in the world","olivia where am i","where am i right now app","what city am i in","my address","which area am i in",'tell me where am i'],

		"weather":["how is weather today","how is the weather in delhi","is it raining today","are clouds today","weather","how much is teamperature","is humidity to high","humidity","temperature","winds","how fast are the winds","sunny weather","cloud weather","humid atmosphere","atomspheric pressure"],

		"alarm reminder":["alarm","reminder","remind me to do","alert for when this happens","remind me after 1 hour to do this","set a reminder for 10 am tomorrow","set an alarm for today 11 am"],

		"schedule" :["shcedule","plan","agenda","meeting","deadline","plan of work","what the schedule for tomorrow","whats the schedule for now","set a meeting with abc at 2pm on thursday this week"],

		"music":["music","song","bgm","play music","play kaho na kaho", "play Ooo.ohh..ooooo", "play pai papa pari parari ba pari","I want to listen sonu's best songs"],

		"find information": ["find information","find me info about this","get me details on that","find profile of nisha pankaj","find every possible thing on elon musk","find details about google company","where did abhinav mishra study","what is the total number of cases for today","who is brother of kiara","how many people died in blm"],

		"message":["message","chat","whatsapp","instagram dm","message bob and tell him i'll be late","inform mom to get dinner ready","inform them to start","inform neha that i am coming",'chat with ajay and find what is he doing'],
		
		"email":["email","email conversation","gmail","microsoft outlook","email bob and tell him i'll be late","mail manish to get ppt ready by tomorrow","email paul and inform him to start","email abc and do","type a mail to bob","send a mail to neha and inform about the updates","email bob and inform him i'll be late"],

		"call":['phone call',"call mom and inform her i'll be late","call puneet and tell him to sell it today","call abc",'handle my all calls and put the phone to bussy mode','address abc with details when you receive call from him','tell john to move when he calls','call','phone puneet and tell him to sell it today','phone abc','phone rebbecaa to inform her about'],
		
		"features":['feature list','what can you do','what are your utilities','tell me about your feature menu','what could you do for me','how good you are','who created you'],

		"translation":['translate','language translate','translate to german','translate to french','change to russion','translate this to english language','language translate'],
#		"calculator":[],
#		"trending news":[''],	
	}

feature_db_encoded = {}
for key,v in feature_db.items():
    feature_db_encoded[key]=model.encode(v)


class shell(Resource):
    def get(self):
        query = request.get_json()['sentence']
        query_embedding = model.encode([query])
        results=[]
        for key,value in feature_db_encoded.items():
            distances = scipy.spatial.distance.cdist(query_embedding, value, "cosine")[0]
            results.append(np.mean(distances))
        results = zip(list(feature_db.keys()), results)
        results = sorted(results, key=lambda x: x[1])
        return jsonify({"Most related feature": results})


api.add_resource(shell,"/")

if __name__ == "__main__":
    app.run(debug=False)
