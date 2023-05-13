from flask import Flask, render_template,session,g,Response,redirect,url_for
from flask_session import Session
from flask import request
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import secrets
import transformers
from transformers import pipeline


app = Flask(__name__)


link=""

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
secret_key = secrets.token_hex(16)
# example output, secret_key = 000d88cd9d90036ebdd237eb6b0db000
app.config['SECRET_KEY'] = secret_key

#front page of website
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/loading',methods=['GET','POST'])
def loading():
    return render_template('loading.html')

@app.route('/result', methods=['GET','POST'])
def result():
    #session.clear()  # Clear session data before starting a new search
    if request.method=="POST":
        
        try:
            url=request.form["link"]
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')
            session['title']=soup.title.text
            para=soup.find_all("p")
            para_text = ""
            for p in para:
                para_text += p.get_text() + " "
            
            ####summarization code:
            summarizer = pipeline("summarization", model="t5-base", tokenizer="t5-base", device=-1)

            session['summary'] = summarizer(para_text, max_length=300, min_length=100, do_sample=False)

    
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
        return render_template('dispDiv.html',summary=session['summary'],title=session['title'])




@app.route('/translate', methods=['GET','POST'])
def translate():
        #session.clear()  # Clear session data before starting a new search
        
        try:
            ####translation code:
            session['value']=request.form.get("trans",False)
            
            translater=Translator()
            para1=session.get('summary')
            
            t1=session.get('title')

            TitleTransLang=translater.translate(t1, dest=session['value'])
            textTitle=TitleTransLang.text
            session['fav_textTitle']=textTitle
            # Extract text from summary
            summary_text = ""
            for s in para1:
                summary_text += s['summary_text']

            # Store summary_text in session
            summ_text = summary_text
            session['fav_summ_text']=summ_text

            ParaTransLang=translater.translate(summ_text, dest=session['value'])
            textPara=ParaTransLang.text
            session['fav_textPara']=textPara
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
        return render_template('translate.html', textTitle=textTitle,textPara=textPara)

@app.route('/cancel', methods=['GET','POST'])
def cancel():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(debug=True)