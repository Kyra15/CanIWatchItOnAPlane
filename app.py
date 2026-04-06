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
                "content": f"""Using this content, extract a summary of the mature content in this. This ONLY pertains to frequent, excessively sexual or extremely gory content. It should be 3-5 sentences long and should contain no specific plot points or characters.
                    You must respond with exactly one of the following:
                    - A 3-5 sentence summary of the mature content. Use language suitable for a teenager.
                    - The exact phrase: no mature content found
                    - The exact phrase: content restricted

                    Use 'content restricted' ONLY if you are unable to summarize due to the nature of the content itself. Do not use it because of missing or unclear data.

                    Content: {info['parentguide']}""",
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
                "content": f"""Classify whether the following movie content summary is 'mature' or 'not mature'.

                    'Mature' means: graphic/explicit depictions of sex, explicit nudity, or extremely gory violence.
                    'Not mature' means: implied or non-explicit sexual content, kissing, making out, references or jokes about sex, non-graphic nudity, or mild violence.
                    
                    Respond only with 'mature' or 'not mature'.
                    If the summary says 'content restricted', output 'mature'.
                    Summary: {final_summ}""",
            }
        ],
        model="llama-3.1-8b-instant",
    )

    info["verdict"] = verdict.choices[0].message.content.lower()
    print("verdict", verdict.choices[0].message.content)

    return render_template("item.html", info=info)

if __name__ == '__main__':
    app.run(port=4200, debug=True)