from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def template():
    return render_template("index.html")


def search():
    # use free imdb api
    # find name based on search
    # check attributes to get id based on name
    # search for parents guide or use attributes wtvs there
    # use some model to ask 
    # given the criteria of "apperance or implications of sex, excessive kissing, nudity" 
    # if its appropriate to watch on a plane
    # OR manually check content levels to see if bad content levels are high
    pass

if __name__ == '__main__':
    app.run(port=4200, debug=True)
