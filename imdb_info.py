import requests
import json
import re

def get_movie_info(movie_id):
    """Extract movie information from IMDb page"""
    imdb_url = f"https://www.imdb.com/title/{movie_id}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(imdb_url, headers=headers)
    response.raise_for_status()
    
    # Find the JSON-LD script tag
    pattern = r'<script type="application/ld\+json">\s*({.*?})\s*</script>'
    match = re.search(pattern, response.text, re.DOTALL)
    
    if not match:
        return None
    
    try:
        data = json.loads(match.group(1))
        print("data", data)
        
        # Extract all available info from JSON-LD
        info = {
            'id': movie_id,
            'title': data.get('name'),
            'description': data.get('description'),
            'aggregateRating': data.get('aggregateRating', {}),
            'directors': [{'name': director.get('name'), 'url': director.get('url')} for director in data.get('director', [])],
        }
        
        return info
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing data: {e}")
        return None
    

def parents_guide_examples(data, include_spoilers=False):
    def collect(categories):
        out = {}
        for cat in categories:
            cid = cat["category"]["id"]
            edges = cat.get("guideItems", {}).get("edges", [])
            out.setdefault(cid, []).extend(
                e["node"]["text"]["plaidHtml"]
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

        print("dict vals", info.values())
        
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

if __name__ == "__main__":
    # Example movie ID
    movie_id = "tt5950044"
    
    print(f"Fetching movie info for {movie_id}...")
    # movie_info = get_movie_info(movie_id)
    movie_info = get_parent_guide(movie_id)
    
    # if movie_info:
    #     filename = f"{movie_id}_info.json"
    #     save_movie_info(movie_info, filename)
        
    #     print(f"\nMovie: {movie_info.get('title')}")
    #     print(f"Year: {movie_info.get('year')}")
    #     print(f"Rating: {movie_info.get('rating')}")
    #     print(f"Genres: {', '.join(movie_info.get('genres', []))}")
    # else:
        # print("Failed to extract movie information")