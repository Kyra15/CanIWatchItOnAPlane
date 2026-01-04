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
                "type": type_of.title(),
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

def spoiler_req(movie_id, category_id):

    payload = {
        "operationName": "TitleParentalGuideCategoryItems",
        "variables": {
            "tconst": movie_id,
            "categoryId": category_id,
            "first": 10,
            "spoilers": "SPOILERS_ONLY",
            "locale": "en-US",
            "inIframeLinkContext": {
                "business": "consumer",
                "isInIframe": True,
                "returnUrl": "https://www.imdb.com/close_me"
            },
            "notInIframeLinkContext": {
                "business": "consumer",
                "isInIframe": False,
                "returnUrl": "https://www.imdb.com"
            }
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "ef99fff1123bdf20351dab6a3926cd3caf7b3ec91a364a708775b8bc2eda77e4"
            }
        }
    }
    
    spo_url = "https://caching.graphql.imdb.com/"
    spo_headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://www.imdb.com/',
        'referer': 'https://www.imdb.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
    }
    spo_req = requests.post(spo_url, headers=spo_headers, json=payload)
    spo_req.raise_for_status()
    data = spo_req.json()

    edges = data["data"]["title"]["parentsGuide"]["guideItems"]["edges"]
    spoilers = [html.unescape(e["node"]["text"]["plaidHtml"]) for e in edges]
    return spoilers


def parents_guide_examples(data, movie_id):
    def collect(categories):
        out = {}
        for cat in categories:
            cid = cat["category"]["id"]
            if cid != "NUDITY":
                continue
            edges = cat.get("guideItems", {}).get("edges", [])
            out.setdefault(cid, []).extend(
                html.unescape(e["node"]["text"]["plaidHtml"])
                for e in edges
                if e.get("node", {}).get("text")
            )
        return out

    examples = collect(data.get("nonSpoilerCategories", []))

    # spoiler shenanigans
    tags = ["NUDITY"]

    for i in tags:
        examples[i] = examples[i] + spoiler_req(movie_id, i)
    # print(examples)

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
        # print("bleh", metadata['directorsPageTitle'])

        info = {
            'id': movie_id,
            'title': metadata.get('titleText', {})['text'],
            'year': metadata.get('releaseYear', {})['year'],
            'img': (metadata.get('primaryImage') or {}).get('url', ''),
            'aggregateRating': (metadata.get('ratingsSummary', {}) or {}).get('aggregateRating', ''),
            'directors': [director["name"]["nameText"]["text"] for director in metadata['directorsPageTitle'][0]["credits"]] if len(metadata['directorsPageTitle']) > 0 else ["Unknown"],
            'categories': [{(c.get("category") or {}).get("id", ""): (c.get("severity") or {}).get("text", "n/a") } for c in (title_data.get("parentsGuide") or {}).get("categories") or [] if c],
            'examples': [{(s.get("category") or {}): s.get("examples") or ["n/a"]} for s in parents_guide_examples(title_data["parentsGuide"] or {}, movie_id) if s]
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


# searched = search_all("oppenheimer")
# results = format_results(searched)
# # print(results)

# movie_id = results[0]["id"]
# get_parent_guide(movie_id)
# print("info", get_parent_guide(movie_id))

