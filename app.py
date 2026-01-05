from flask import Flask, render_template, request
from summarizer import summarize_examples, final_pass, classify
from imdb_full import *
from csm_search import *
import os 
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, pipeline
import torch

os.environ["TOKENIZERS_PARALLELISM"] = "false"

import psutil
import os
import threading
import time

def log_memory():
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / 1024 / 1024
        print(f"[MEMORY] {mem:.2f} MB")
        time.sleep(5)

threading.Thread(target=log_memory, daemon=True).start()


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
    results = []
    if request.method == 'POST':
        query = request.form.get("query")
        print("user searched:", query)

        searched = search_all(query)
        results = format_results(searched)
    return render_template("index.html", results_list=results)

@app.route('/<title_id>')
def item(title_id):
    imdb_info = get_parent_guide(title_id)

    # csm_str = str(imdb_info.get("title", ""))
    # csm_url = csm_search(csm_str)
    # print(csm_url)
    # first_op = list(csm_url.keys())[0]
    # csm_info = get_info(first_op)
    # csm_tags = ['to_know', 'violence_scariness', 'sex_romance_nudity', 'drinking_drugs_smoking']
    # csm_formatted_str = " ".join([csm_info.get(x, "") for x in csm_tags])
    # print("ahisdhaosidjoaisd", csm_formatted_str)
    # need to figure out how to get year so i can confirm diff movies n stuff

    imdb_str_lst = []
    for i in imdb_info["examples"]:
        for j in i.values():
            imdb_str_lst.extend(j)
    imdb_formatted_str = " ".join(imdb_str_lst)
    # print("hello", imdb_formatted_str)

    summ = summarize_examples(model, imdb_formatted_str, shared_tokenizer)
    # print("hi2345", summ)

    if summ == "No significant content found.":
        imdb_info["verdict"] = "YES"
        final = "No significant mature content found."
        imdb_info["summary"] = final
        return render_template("item.html", info=imdb_info)
    
    verdict = classify(summ, pipe)
    imdb_info["verdict"] = verdict.strip().upper()
    # print("verdict", verdict)
    final = final_pass(summ, pipe)
    # print("final", final)
    imdb_info["summary"] = final
    return render_template("item.html", info=imdb_info)

if __name__ == '__main__':
    app.run(port=4200, debug=False)

    shared_tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-1.7B-Instruct")

    pipe = pipeline(
        "text-generation",
        model="HuggingFaceTB/SmolLM2-1.7B-Instruct",
        model_kwargs={
            "dtype": torch.float16,
            "low_cpu_mem_usage": True,
        },
        device="cpu",
        tokenizer=shared_tokenizer
    )

    model = SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu"
    )


    # use free imdb api
    # find name based on search
    # check attributes to get id based on name
    # search for parents guide or use attributes wtvs there
    # use some model to ask 
    # given the criteria of "apperance or implications of sex, excessive kissing, nudity" 
    # if its appropriate to watch on a plane
    # OR manually check content levels to see if bad content levels are high
