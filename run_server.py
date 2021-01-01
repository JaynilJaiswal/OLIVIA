from flask import Flask,render_template,request,redirect,url_for,session

import jsonify
app = Flask(__name__)
app.secret_key = 'random'
@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='GET':
        # global play
        session['play']=0
        print(session['play'])
        return render_template('index.html',play=session['play'])
    if request.method=='POST':
        f  = request.files['audio_data']
        # print(f)
        with open(f.filename,'wb') as audio:
            # f.save
            f.save(audio)
        # global play
        session['play']=1
        print(session['play'])
        # return redirect(url_for('home',play=play))
        # return render_template('index.html',play=session['play'])
        return redirect(url_for('process'))
    # return render_template('index.html',play=session['play'])

@app.route('/process',methods=['GET','POST'])
def process():
    if request.method=='GET':
        print(session['play'])
        return render_template('process.html',play=session['play'])
    # return render_template('process.html',play=session['play'])

#     if request.method=='POST':
#         f  = request.files['audio_data']
#         # print(f)
#         with open(f.filename,'wb') as audio:
#             # f.save
#             f.save(audio)
#         global play
#         play=1
#         return redirect(url_for('home',play=play))
        # return render_template('index.html',play=play)

if __name__ == "__main__":
    app.run(debug=True)