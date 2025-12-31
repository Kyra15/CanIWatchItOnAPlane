import bs4
import requests
import re
import pandas as pd
import os

# search url https://www.commonsensemedia.org/search/supergirl

def csm_search(phrase):
    phrase = phrase.replace(" ", "%20")
    url = "https://www.commonsensemedia.org/search/{}".format(phrase)
    # ajax: https://www.commonsensemedia.org/ajax/search/five%20nights%20at%20freddys

    ajax_url = "https://www.commonsensemedia.org/ajax/search/{}".format(phrase)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15",
        "Accept": "application/json",
        "Referer": url
    }

    response = requests.get(ajax_url, headers=headers)
    ajax_data = response.json()

    html_content = ""
    for cmd in ajax_data:
        if cmd.get("command") == "insert":
            html_content += cmd.get("data", "")

    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    movie_links = soup.find_all('a', class_="link--title", href=re.compile('^' + "/movie-reviews/"))
    tv_links = soup.find_all('a', class_="link--title", href=re.compile('^' + "/tv-reviews/"))

    print(movie_links)

    options_dict = {}
    for link in movie_links:
        b = "https://www.commonsensemedia.org"
        name = link.text
        # year = 
        link = link.get('href')
        url = b + link
        if url not in list(options_dict.keys()):
            options_dict.update({url: [name]})

    for link in tv_links:
        b = "https://www.commonsensemedia.org"
        name = link.text
        # year = 
        link = link.get('href')
        url = b + link
        if url not in list(options_dict.keys()):
            options_dict.update({url: [name]})
    
    return options_dict


def cl_search_txt(soup, class_str, index = 0):
    container = soup.select(class_str)
    return container[index].text


def get_info(url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15",
    }

    page = requests.get(url, headers=headers)

    if page.status_code == 200:
        soup = bs4.BeautifulSoup(page.content, "html.parser")

        date = soup.find("span", class_="detail--release-dates-theaters")
        year = date.text.strip()[-4:]
        # separate conditions if the movie is not out yet
        if len(soup.find_all("div", class_="review-view-coming-soon")) > 0:
            return {
                "to_know": "This movie has yet to come out! This page will update when it does and we have more info :)",
                "year": "n/a",
                "cs_age": "n/a",
                "comm_age": "n/a",
            }
        else:
            h1_tag = [h for h in soup.select("h3") if h.get_text(strip=True) == "Parents Need to Know"][0]
            content_div = h1_tag.find_next_sibling("div")
            to_know = content_div.find("p")
            for a in to_know.find_all("a"):
                a.replace_with(a.get_text())
            # print(to_know)
            # save_dict.update({"to_know": to_know.text})

            age = cl_search_txt(soup, "span[class^=rating__age]")
            age = age.strip()
            # print("CSM age rating:", age)

            cs_age = "n/a"
            if age:
                non_decimal = re.compile(r'[^\d.]+')
                cs_age = non_decimal.sub('', age)
            # save_dict.update({"cs_age": int(cs_age)})

            p_age = "n/a"
            if len(soup.select("span[class^=rating__age]")) > 1:
                p_age = cl_search_txt(soup, "span[class^=rating__age]",1)
                p_age = p_age.strip()
                # print("Community age rating", p_age)
                p_age = non_decimal.sub('', p_age)
                # save_dict.update({"comm_age": int(p_age)})
            
            save_dict = {}
            subjects = ["Violence & Scariness", "Sex, Romance & Nudity", "Drinking, Drugs & Smoking"]
            for i in subjects:
                sub_tag = [h for h in soup.select("h3") if h.get_text(strip=True) == i][0]
                # print(sub_tag.text)
                content = sub_tag.find_next_sibling("p")
                cleaned = re.sub(r'[^a-zA-Z\s]', '', i)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                save_dict.update({cleaned.lower().replace(" ", "_"): content.text})
    final = {"to_know": to_know.text,
             "year": year,
             "cs_age": cs_age,
             "comm_age": p_age}
    final.update(save_dict)
    return final


# temp_dict = {}
# final_dict = {}

# urls = csm_search("oppenheimer")
# # print(urls)
# searched = get_info(list(urls)[0])
# print(searched)

# df = pd.DataFrame(
#     temp_dict.items(),
#     columns=["category", "content"]
# )

# df.to_csv("csm_search_result.csv", index=False)