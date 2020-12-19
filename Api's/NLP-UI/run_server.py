from flask import Flask, request
from flask_restful import Api,Resource,reqparse
from sentence_transformers import SentenceTransformer
import scipy
import numpy as np

app= Flask(__name__)
api=Api(app)
model = SentenceTransformer('bert-base-nli-mean-tokens')
feature_db = { "insane":['Absence of sanity', 'Lack of saneness'],
                "rocket" : ['Launch','Build']}
sentence = ['Absence of sanity', 
             'Lack of saneness',
             'A man is eating food.',
             'A man is eating a piece of bread.',
             'The girl is carrying a baby.',
             'A man is riding a horse.',
             'A woman is playing violin.',
             'Two men pushed carts through the woods.',
             'A man is riding a white horse on an enclosed ground.',
             'A monkey is playing drums.',
             'A cheetah is running behind its prey.',
             'Get me updates on stock market',
             'Get me updates on rupee market',
             "get me details of",
            "1. Abstractive Model",
            "2. Extractive Model",
             "linux",
            "Launch",
            "Build"]
feature_db_encoded = {}
for key,v in feature_db.items():
    feature_db_encoded[key]=model.encode(v)

# sentence_embeddings = model.encode(sentence)

class hello(Resource):
    def get(self):
        print(request.args['input_str'])
        query=request.args['input_str']
        query_embedding = model.encode([query])
        results=[]
        for key,value in feature_db_encoded.items():
            distances = scipy.spatial.distance.cdist(query_embedding, value, "cosine")[0]
            results.append(np.mean(distances))
        results = zip(list(feature_db.keys()), results)
        results = sorted(results, key=lambda x: x[1])
        return {"result": results[0][0]}

api.add_resource(hello,"/")

if __name__ == "__main__":
    app.run(debug=True)
