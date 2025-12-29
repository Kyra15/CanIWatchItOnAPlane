from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer, util
import re
import torch
from imdb_full import *
from csm_search import *
import os 
from summarizer import summarize_examples

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
model = SentenceTransformer("all-MiniLM-L6-v2")

@app.route("/")
def template():
    return render_template("index.html")

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/search', methods=['GET', 'POST'])
def search():

    if request.method == 'POST':
        query = request.form.get("query")
        print("user searched:", query)

        searched = search_all(query)
        results = format_results(searched)

    return render_template("index.html", results_list=results)

@app.route('/<title_id>')
def item(title_id):
    imdb_info = get_parent_guide(title_id)
    csm_str = str(imdb_info.get("title", "")) + " " + str(imdb_info.get("year", ""))
    csm_url = csm_search(csm_str)
    first_op = list(csm_url.keys())[0]
    csm_info = get_info(first_op)
    # print("hi", csm_info)
    return render_template("item.html", info=imdb_info)

if __name__ == '__main__':
    app.run(port=4200, debug=True)


    # use free imdb api
    # find name based on search
    # check attributes to get id based on name
    # search for parents guide or use attributes wtvs there
    # use some model to ask 
    # given the criteria of "apperance or implications of sex, excessive kissing, nudity" 
    # if its appropriate to watch on a plane
    # OR manually check content levels to see if bad content levels are high
