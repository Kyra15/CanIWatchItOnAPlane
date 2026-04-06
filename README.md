# Can I Watch It On A Plane?
A web app for people who want to know if a movie is too mature before watching it at 30,000 feet in front of the other passengers on your plane (or anywhere, really). Search any movie, get a plain-English verdict on the mature content without spoilers.

## How it works:
1. Go to [caniwatchitonaplane.onrender.com](https://caniwatchitonaplane.onrender.com)
2. Search for a movie by title
3. Click on a result
4. Get a spoiler-free summary of any sexual or gory content, plus a verdict: **mature** or **not mature**

The app pulls parental guide data from IMDB, sends it to the Groq API (Llama 3.1), and returns a plain-English content summary with a classification with no plot points or spoilers.

## To run this locally:
1. Clone this repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your keys:

## Todo:
- Write comments
- Speed the summarizing process up
