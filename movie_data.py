import csv
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import pandas as pd


def cl_search_txt(soup, class_str, index = 0):
    container = soup.select(class_str)
    return container[index].text


def restrip(str, find, replace=""):
    out = str.replace(find, replace)
    return out.strip()


def text_add(str, add, pretext="\n"):
    return str + pretext + add

def scrape_CSM_page(movie_dict, url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15",
    }

    page = requests.get(url, headers=headers)

    if page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        # separate conditions if the movie is not out yet
        if len(soup.find_all("div", class_="review-view-coming-soon")) > 0:
            print("This movie has yet to come out! This page will update when it does and we have more info :)")
        else:
            h1_tag = [h for h in soup.select("h3") if h.get_text(strip=True) == "Parents Need to Know"][0]
            content_div = h1_tag.find_next_sibling("div")
            to_know = content_div.find("p")
            for a in to_know.find_all("a"):
                a.replace_with(a.get_text())
            # print(to_know)
            movie_dict.update({"to_know": to_know})

            age = cl_search_txt(soup, "span[class^=rating__age]")
            age = age.strip()
            # print("CSM age rating:", age)

            non_decimal = re.compile(r'[^\d.]+')
            cs_age = non_decimal.sub('', age)
            movie_dict.update({"cs_age": int(cs_age)})

            if len(soup.select("span[class^=rating__age]")) > 1:
                p_age = cl_search_txt(soup, "span[class^=rating__age]",1)
                p_age = p_age.strip()
                # print("Community age rating", p_age)
                p_age = non_decimal.sub('', p_age)
                movie_dict.update({"comm_age": int(p_age)})

            # div = soup.select("div[class^=content-grid-item]")
            # text = "[Common Sense Media]"
            # text = text_add(text, age, " ")
            # text = text_add(text, to_know, "\n")
            # # print(text)
            # for d in div:
            #     x = restrip(d.text, "Not present", "")
            #     s = d["data-text"]
            #     s = re.sub('<[^>]*>', '', s)
            #     s = re.sub('Did you know [^?.!]*[?.!]', '', s)
            #     s = re.sub('Adjust limits [^?.!]*[?.!]', '', s)
            #     s = restrip(s, "Join now")
            #     s = s.strip()
            #     text = text_add(text, x, "\n|")
            #     text = text_add(text, s, "|: ")
            # now = datetime.now()
            # text = restrip(text, "\n\n\n", "\n")
            # text = restrip(text, "\n\n", "\n")
            # text = restrip(text, "\n\n", "\n")
            # text = text_add(text, "[Date:" + now.strftime('%Y-%m-%d') + "]")
            # movie_dict.update({'cs_summary': text})
    else:
        print(page.status_code, "ERROR BAD STATUS CODE")
    return movie_dict

with open("url_list.txt", "r") as f:
    movie_list = [line.strip() for line in f]

movie_dict = {}
for i in movie_list:
    print(i)
    scrape_CSM_page(movie_dict, i)

df = pd.DataFrame.from_dict(movie_dict, index=None)
df.to_csv("csm_movies.csv")
