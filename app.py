from flask import Flask, render_template, request

app = Flask(__name__)
app.config['SECRET_KEY'] = "9e7571b29e4f280b8e76bc8cd0b99e8b26862fa5448cb8c8"

@app.route("/")
def template():
    return render_template("index.html")

@app.route('/search', methods=['GET', 'POST'])
def search():

    results_list = []

    if request.method == 'POST':
        query = request.form.get("query")
        print("user searched:", query)

        # call functions    
        results_list = [{"title": "Supergirl", "year": "2026", "dir": "James Gunn"}, {"title": "Little Women", "year": "2019", "dir": "Greta Gerwig"}]

    return render_template("index.html", results_list=results_list)

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
