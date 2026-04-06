from flask import Flask, render_template, request
# from summarizer import summarize_examples, final_pass, classify
from imdb_full import *
# from csm_search import *
from dotenv import load_dotenv
import os 
from groq import Groq

load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
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
    # imdb_info = get_parent_guide(title_id)
    # print("hihi", imdb_info)
    # print(get_info(title_id))
    info = get_info(title_id)
    print("hi", info)

    summ = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Using this content, extract a summary of the mature content in this. This ONLY pertains to excessively sexual or extremely gory content. It should be 3-5 sentences long and should contain no specific plot points or characters. If there is no mature content, return 'no mature content found'. Content: {info['parentguide']}",
            }
        ],
        model="llama-3.1-8b-instant",
        temperature=0,
    )

    print("hola", summ.choices[0].message.content)

    final_summ = summ.choices[0].message.content
    info["summary"] = final_summ

    verdict = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Using this summary, classify this movie as either mature or not mature. 'Mature' should only be returned when the text given includes overly-excessive mature content. Return only: mature or not mature. Summary: {final_summ}",
            }
        ],
        model="llama-3.1-8b-instant",
    )

    info["verdict"] = verdict.choices[0].message.content
    print("verdict", verdict.choices[0].message.content)

    return render_template("item.html", info=info)

if __name__ == '__main__':
    app.run(port=4200, debug=True)