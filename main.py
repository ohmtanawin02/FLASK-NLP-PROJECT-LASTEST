from flask import Flask, render_template, request,redirect
from werkzeug.utils import secure_filename
import os
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.tokenize import word_tokenize
from collections import Counter
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from gensim.corpora.dictionary import Dictionary
from collections import defaultdict
import itertools
from gensim.models.tfidfmodel import TfidfModel
from flask import Flask,url_for,render_template,request
import spacy
from spacy import displacy
nlp = spacy.load('en_core_web_sm')
import json

HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem">{}</div>"""

from flaskext.markdown import Markdown

app = Flask(__name__)
Markdown(app)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = 'static/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
articles = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template("upload.html")

@app.route('/show', methods = ['GET', 'POST'])
def upload_file():
    #if request.method == 'POST' in request.files:
    #    for f in request.files:
    #        f.save(os.path.join(app.config['UPLOAD_PATH'], f.filename))
    #    return 'Upload completed.'
    #return render_template('uploader.html')
    if request.method == 'POST':
            f = request.files['file']
            filename = secure_filename(f.filename)
            f.save(app.config['UPLOAD_FOLDER'] + filename)

            file = open(app.config['UPLOAD_FOLDER'] + filename,"r")
            content = file.read()   
            
    return render_template('content.html', content=content) 
@app.route('/search', methods = ['GET', 'POST'])
def use_file():
    if request.method == 'POST':
        word = request.form['word']
        dir_path = r'static'
        count = 0
        # Iterate directory
        for path in os.listdir(dir_path):
        # check if current path is a file
            if os.path.isfile(os.path.join(dir_path, path)):
                count += 1
    articles = []
    for i in range(count):
        f = open(f"wiki_article_{i}.txt", "r")
        article = f.read()
        tokens = word_tokenize(article)
        lower_tokens = [t.lower() for t in tokens]
        alpha_only = [t for t in lower_tokens if t.isalpha()]
        no_stops = [t for t in alpha_only if t not in stopwords.words('english')]
        wordnet_lemmatizer = WordNetLemmatizer()
        lemmatized = [wordnet_lemmatizer.lemmatize(t) for t in no_stops]
        articles.append(lemmatized)
    dictionary = Dictionary(articles)
    #print(dictionary)
    word_id = dictionary.token2id.get(word)
    msg = word
    msg3 = 'has word :'
    msg4 = word_id
    return render_template('upload.html',msg = msg,msg3 = msg3,msg4 = msg4)

@app.route('/topfive', methods = ['GET', 'POST'])
def serchtopfiveword():
    if request.method == 'POST':
        dir_path = r'static'
        count = 0
        # Iterate directory
        for path in os.listdir(dir_path):
        # check if current path is a file
            if os.path.isfile(os.path.join(dir_path, path)):
                count += 1
    articles = []
    for i in range(count):
        f = open(f"wiki_article_{i}.txt", "r")
        article = f.read()
        tokens = word_tokenize(article)
        lower_tokens = [t.lower() for t in tokens]
        alpha_only = [t for t in lower_tokens if t.isalpha()]
        no_stops = [t for t in alpha_only if t not in stopwords.words('english')]
        wordnet_lemmatizer = WordNetLemmatizer()
        lemmatized = [wordnet_lemmatizer.lemmatize(t) for t in no_stops]
        articles.append(lemmatized)
    dictionary = Dictionary(articles)
    corpus = [dictionary.doc2bow(a) for a in articles]
    doc = corpus[0]
    tfidf = TfidfModel(corpus)
    tfidf_weights = tfidf[doc]
    sorted_tfidf_weights = sorted(tfidf_weights, key=lambda w: w[1], reverse=True)
    msgtop = []
    for term_id, weight in sorted_tfidf_weights[:5]:
        a = dictionary.get(term_id), weight
        msgtop.append(a)
    return render_template('uploadyet.html', msgtop = msgtop)

@app.route('/extract',methods=["GET","POST"])
def extract():
	if request.method == 'POST':
		raw_text = request.form['rawtext']
		docx = nlp(raw_text)
		html = displacy.render(docx,style="ent")
		html = html.replace("\n\n","\n")
		result = HTML_WRAPPER.format(html)

	return render_template('result.html',rawtext=raw_text,result=result)
#def use():
#    for i in range(10):
    # Read TXT file
#        f = open(f"static\wiki_article_{i}.txt", "r")
#        article = f.read()
        # Tokenize the article: tokens
#        tokens = word_tokenize(article)
        # Convert the tokens into lowercase: lower_tokens
#        lower_tokens = [t.lower() for t in tokens]
        # Retain alphabetic words: alpha_only
#        alpha_only = [t for t in lower_tokens if t.isalpha()]
        # Remove all stop words: no_stops
#        no_stops = [t for t in alpha_only if t not in ("english")]
        # Instantiate the WordNetLemmatizer
#        wordnet_lemmatizer = WordNetLemmatizer()
        # Lemmatize all tokens into a new list: lemmatized
#        lemmatized = [wordnet_lemmatizer.lemmatize(t) for t in no_stops]
        # list_article
#        articles.append(lemmatized)
#    dictionary = Dictionary(articles)
#    computer_id = dictionary.token2id.get("computer")
#    corpus = [dictionary.doc2bow(a) for a in articles]
#    doc = corpus[9]
#    tfidf = TfidfModel(corpus)
#    tfidf_weights = tfidf[doc]
#    #print(tfidf_weights[:5])
#    sorted_tfidf_weights = sorted(tfidf_weights, key=lambda w: w[1], reverse=True)
#    for term_id, weight in sorted_tfidf_weights[:5]:
#        print((f"<p> {dictionary.get(term_id), weight} </p>"))
        

if __name__ == '__main__':
    app.run(debug=True)