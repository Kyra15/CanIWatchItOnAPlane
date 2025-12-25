import bs4
import requests
import re

# look for the next data tag and yoink all of that


# Listing page for movies
page_num = 0
url = 'https://www.commonsensemedia.org/search/category/movie/page/{}'.format(page_num)
total_page = 3


'''
header:
https://www.commonsensemedia.org/ajax/search/category/movie/page/0?ajax_page_state[libraries]=eJyVk22SwiAMhi9k7JE6KU0pIyQdktrx9stUXVftWvzDTMjzhpAPJykJt0qs1LjVOAU7-hz6g9v2qV0i6bN3EN50tIn6gK2NlKjxUTqMDyyvUSdhYtPjXxmAO8EgOYErgbPEfTok9LSPxcCnPUrL02KUaznATmarpp1Mlxz8WK9IxHM1zLRoJPsmfyXMbqzHxQWMoCPm3YorjIR9EUVkP5cWgS7B3FiT3U2ZMHBlCW4KkwkYz--8pvZhwh3_7_svdKZzoAWMULeyf6GvQdfkv2FhCHGzdbuSjY36oIlBN-bvg6DUtJavrNBcIJji_Nu2DpmLzov4SK2hb3w5nu10mPqu0WD0Nh7NbWtfgfWdOuB6cdCLGqWmK9_4Ae-t-eQ

method:
GET

agent:
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15

:authority
www.commonsensemedia.org
:method
GET
:path
/ajax/search/category/movie/page/0?ajax_page_state[libraries]=eJyVk22SwiAMhi9k7JE6KU0pIyQdktrx9stUXVftWvzDTMjzhpAPJykJt0qs1LjVOAU7-hz6g9v2qV0i6bN3EN50tIn6gK2NlKjxUTqMDyyvUSdhYtPjXxmAO8EgOYErgbPEfTok9LSPxcCnPUrL02KUaznATmarpp1Mlxz8WK9IxHM1zLRoJPsmfyXMbqzHxQWMoCPm3YorjIR9EUVkP5cWgS7B3FiT3U2ZMHBlCW4KkwkYz--8pvZhwh3_7_svdKZzoAWMULeyf6GvQdfkv2FhCHGzdbuSjY36oIlBN-bvg6DUtJavrNBcIJji_Nu2DpmLzov4SK2hb3w5nu10mPqu0WD0Nh7NbWtfgfWdOuB6cdCLGqWmK9_4Ae-t-eQ
:scheme
https
'''


def grab_movies(page_num, is_movie):
    url_match = "/movie-reviews/" if is_movie else "/tv-reviews/"
    ajax_url = f"https://www.commonsensemedia.org/ajax/search/category/movie/page/{page_num}" if is_movie else f"https://www.commonsensemedia.org/ajax/search/category/tv/page/{page_num}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15",
        "Accept": "application/json",
        "Referer": f"https://www.commonsensemedia.org/search/category/movie/page/{page_num}" if is_movie else f"https://www.commonsensemedia.org/search/category/tv/page/{page_num}"
    }

    response = requests.get(ajax_url, headers=headers)
    ajax_data = response.json()

    html_content = ""
    for cmd in ajax_data:
        if cmd.get("command") == "insert":
            html_content += cmd.get("data", "")

    soup = bs4.BeautifulSoup(html_content, 'html.parser')

    links = soup.find_all('a', href=re.compile('^' + url_match))
    urls = []
    for link in links:
        b = "https://www.commonsensemedia.org"
        link = link.get('href')
        url = b + link
        if url not in urls:
            urls.append(url)
    return urls


total_list = []

for i in range(10):
    total_list.extend(grab_movies(i, True))

print(total_list)

with open("url_list.txt", "w") as f:
    f.write("\n".join(total_list))