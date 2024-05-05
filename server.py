from flask import Flask, jsonify, render_template ,request
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from sqlite3 import Error
from datetime import datetime
from flask import Flask, redirect, url_for, render_template, request

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

df = pd.read_csv("corona.csv")
connection = create_connection('data.db')
df.to_sql('corona_data', connection, if_exists='replace')
connection.close()

db_url = 'sqlite:///data.db'
engine = create_engine(db_url, echo=True)

app = Flask(__name__)


#Import the necessary modules:
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import *
from nltk.stem.porter import *
import pandas as pd
import re # used to clean the data
#to display the full text on the notebook without truncation
pd.set_option('display.max_colwidth', 150)
# Initialize Porter stemmer
stemmer = PorterStemmer()

nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))
import pyterrier as pt
if not pt.started():
  pt.init()
def Stem_text(text):
    tokens = word_tokenize(text)
    stemmed_tokens = [stemmer.stem(word) for word in tokens]
    # print (tokens)
    return ' '.join(stemmed_tokens)

def clean(text):
   text = re.sub(r"[\.\,\#_\|\:\?\?\/\=\@]", " ", text) # remove special characters
   text = re.sub(r'\t', ' ', text) # remove tabs
   text = re.sub(r'\n', ' ', text) # remove line jump
   text = re.sub(r"\s+", " ", text) # remove extra white space
   text = text.strip()
   return text

def remove_stopwords(text):
    tokens = word_tokenize(text)
    filtered_tokens = [word.lower() for word in tokens if word.lower() not in stop_words] #Lower is used to normalize al the words make them in lower case
    # print('Tokens are:',tokens,'\n')
    return ' '.join(filtered_tokens)

#we need to process the query also as we did for documents
def preprocess(sentence):
  sentence = clean(sentence)
  sentence = remove_stopwords(sentence)
  sentence = Stem_text(sentence)
  return sentence

res = df['OriginalTweet'].apply(preprocess)
df['docno'] = df["ScreenName"].astype(str)
pd_indexer = pt.DFIndexer("./pd_index1")
indexref = pd_indexer.index(df["OriginalTweet"], df["docno"])

index = pt.IndexFactory.of(indexref)


word_to_documents = {}

inv = index.getInvertedIndex()
meta = index.getMetaIndex()

for kv in index.getLexicon():
    term = kv.getKey()
    pointer = index.getLexicon()[term]
    doc_ids = []
    for posting in inv.getPostings(pointer):
        docno = meta.getItem("docno", posting.getId())
        doc_ids.append(docno)

    word_to_documents[term] = doc_ids

# for term, doc_ids in word_to_documents.items():
#     print("%s -> %s (%d occurrences)" % (term, doc_ids, len(doc_ids)))





@app.route('/search',methods=["POST","GET"])
def search():
  return render_template('search.html')



if __name__ == '__main__':
    app.run(debug=True, port=3001)