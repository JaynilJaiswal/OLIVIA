from deepcorrect import DeepCorrect
from flask import Flask, request, jsonify
from flask_restful import Api,Resource,reqparse

app= Flask(__name__)
api=Api(app)

corrector = DeepCorrect('DeepCorrect_PunctuationModel/deeppunct_params_en', 'DeepCorrect_PunctuationModel/deeppunct_checkpoint_google_news')

class pre_process(Resource):
	def get(self):
		text=request.args['input_str']

		if 'olivia' in text:
			text = text.split('olivia')[1].strip()
		if 'olvia' in text:
			text = text.split('olvia')[1].strip()
		if 'oliva' in text:
			text = text.split('oliva')[1].strip()
		if 'holivia' in text:
			text = text.split('holivia')[1].strip()

		text = corrector.correct(text)
		print(text)
		return text


api.add_resource(pre_process,"/")

if __name__ == "__main__":
	app.run(host='127.0.0.1',port=5040,debug=True)