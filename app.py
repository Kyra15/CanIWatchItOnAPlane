from flask import Flask, render_template, request
from summarizer import summarize_examples, final_pass, classify
from imdb_full import *
from csm_search import *
import os 
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, pipeline
import torch

os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

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
    print("hihi", imdb_info)

    imdb_str_lst = []
    for i in imdb_info["examples"]:
        for j in i.values():
            imdb_str_lst.extend(j)
    imdb_formatted_str = " ".join(imdb_str_lst)

    summ = summarize_examples(model, imdb_formatted_str, shared_tokenizer)

    if summ == "No significant content found.":
        imdb_info["verdict"] = "YES"
        final = "No significant mature content found."
        imdb_info["summary"] = final
        return render_template("item.html", info=imdb_info)
    
    verdict = classify(summ, pipe)
    imdb_info["verdict"] = verdict.strip().upper()
    final = final_pass(summ, pipe)
    imdb_info["summary"] = final
    return render_template("item.html", info=imdb_info)

if __name__ == '__main__':
    app.run(port=4200, debug=True)