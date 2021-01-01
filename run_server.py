from flask import Flask,render_template,request,redirect,url_for


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')
@app.route('/process',methods=['GET','POST'])
def process():
    if request.method=='POST':
        f  = request.files['audio_data']
        # print(f)
        with open(f.filename,'wb') as audio:
            # f.save
            f.save(audio)
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)