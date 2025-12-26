# https://github.com/pavan412kalyan/imdb-movie-scraper/blob/main/ImdbDataExtraction/search_by_string/search_by_string.py


import requests
import json
import html
import re

BASE_URL = "https://v3.sg.media-imdb.com/suggestion"

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://m.imdb.com',
    'priority': 'u=1, i',
    'referer': 'https://m.imdb.com/',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
}

def search_all(query, limit=20):
    """Search using IMDb suggestion API"""
    # Get first letter for the API endpoint
    first_letter = query[0].lower() if query else 'a'
    
    # Build the suggestion URL
    url = f"{BASE_URL}/{first_letter}/{query}.json"
    params = {'includeVideos': '0'}
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code != 200:
        print(f"Response text: {response.text}")
    
    response.raise_for_status()
    return response.json()


def format_results(data, limit=20):
    """Format search results for display"""
    suggestions = data.get("d", [])
    results = []
    
    for item in suggestions[:limit]:
        if not item:
            continue
            
        item_id = item.get("id", "")
        name = item.get("l", "Unknown")
        year = item.get("y")  # Year for titles
        type_of = item.get("q", "Unknown")

        if type_of.lower() == "feature":
            type_of = "Movie"
        
        # Determine if it's a title or person based on ID prefix
        if item_id.startswith("tt"):
            # Title (movie/TV show)
            result = {
                "id": item_id,
                "name": name,
                "year": year,
                "type": type_of
                # "description": description,
                # "image": item.get("i", {}).get("imageUrl") if item.get("i") else None
            }
        # elif item_id.startswith("nm"):
        #     # Person
        #     result = {
        #         "type": "Person",
        #         "id": item_id,
        #         "name": name,
        #         # "description": description,
        #         # "image": item.get("i", {}).get("imageUrl") if item.get("i") else None
        #     }
        else:
            continue
            
        results.append(result)
    
    return results


def parents_guide_examples(data):
    def collect(categories):
        out = {}
        for cat in categories:
            cid = cat["category"]["id"]
            edges = cat.get("guideItems", {}).get("edges", [])
            out.setdefault(cid, []).extend(
                html.unescape(e["node"]["text"]["plaidHtml"])
                for e in edges
                if e.get("node", {}).get("text")
            )
        return out

    examples = collect(data.get("nonSpoilerCategories", []))

    spoiler_examples = collect(data.get("spoilerCategories", []))
    for cid, texts in spoiler_examples.items():
        examples.setdefault(cid, []).extend(texts)

    return [
        {
            "category": cid,
            "examples": texts
        }
        for cid, texts in examples.items()
    ]

    
def get_parent_guide(movie_id):
    url = f"https://www.imdb.com/title/{movie_id}/parentalguide/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    pattern = r'<script id="__NEXT_DATA__" type="application/json">\s*({.*?})\s*</script>'
    match = re.search(pattern, response.text, re.DOTALL)
    
    if not match:
        return None
    
    try:
        data = json.loads(match.group(1))

        metadata = data['props']['pageProps']['contentData']['entityMetadata']
        title_data = data['props']['pageProps']['contentData']["data"]["title"]

        info = {
            'id': movie_id,
            'title': metadata.get('titleText')['text'],
            'year': metadata.get('releaseYear')['year'],
            'img': metadata.get('primaryImage')['url'],
            'aggregateRating': metadata.get('ratingsSummary', {})['aggregateRating'],
            'directors': [director["name"]["nameText"]["text"] for director in metadata['directorsPageTitle'][0]["credits"]],
            'categories': [{c["category"]["id"]: c["severity"]["text"]} for c in title_data["parentsGuide"]["categories"]],
            'examples': [{s["category"]: s["examples"]} for s in parents_guide_examples(title_data["parentsGuide"])]
        }

        # print("dict vals", info.values())
        
        # return info
        return info
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing data: {e}")
        return None
    

def save_movie_info(movie_info, filename):
    """Save movie info to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(movie_info, f, indent=2, ensure_ascii=False)
    print(f"Movie info saved to {filename}")


searched = search_all("superman")
results = format_results(searched)
# print(results)

# movie_id = results[0]["id"]
# print("info", get_parent_guide(movie_id))

