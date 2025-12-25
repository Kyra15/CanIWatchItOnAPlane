import bs4
import requests
import re

# search url https://www.commonsensemedia.org/search/supergirl

def search(phrase):
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
        link = link.get('href')
        url = b + link
        if url not in list(options_dict.keys()):
            options_dict.update({url: name})

    for link in tv_links:
        b = "https://www.commonsensemedia.org"
        name = link.text
        link = link.get('href')
        url = b + link
        if url not in list(options_dict.keys()):
            options_dict.update({url: name})
    
    return options_dict


def cl_search_txt(soup, class_str, index = 0):
    container = soup.select(class_str)
    return container[index].text


def get_info(save_dict, url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15",
    }

    page = requests.get(url, headers=headers)

    if page.status_code == 200:
        soup = bs4.BeautifulSoup(page.content, "html.parser")
        # separate conditions if the movie is not out yet
        if len(soup.find_all("div", class_="review-view-coming-soon")) > 0:
            save_dict.update({"to_know": "This movie has yet to come out! This page will update when it does and we have more info :)"})
            save_dict.update({"cs_age": "n/a"})
            save_dict.update({"comm_age": "n/a"})
        else:
            h1_tag = [h for h in soup.select("h3") if h.get_text(strip=True) == "Parents Need to Know"][0]
            content_div = h1_tag.find_next_sibling("div")
            to_know = content_div.find("p")
            for a in to_know.find_all("a"):
                a.replace_with(a.get_text())
            print(to_know)
            save_dict.update({"to_know": to_know})

            age = cl_search_txt(soup, "span[class^=rating__age]")
            age = age.strip()
            print("CSM age rating:", age)

            non_decimal = re.compile(r'[^\d.]+')
            cs_age = non_decimal.sub('', age)
            save_dict.update({"cs_age": int(cs_age)})

            if len(soup.select("span[class^=rating__age]")) > 1:
                p_age = cl_search_txt(soup, "span[class^=rating__age]",1)
                p_age = p_age.strip()
                print("Community age rating", p_age)
                p_age = non_decimal.sub('', p_age)
                save_dict.update({"comm_age": int(p_age)})
            
            subjects = ["Violence & Scariness", "Sex, Romance & Nudity", "Drinking, Drugs & Smoking"]
            for i in subjects:
                sub_tag = [h for h in soup.select("h3") if h.get_text(strip=True) == i][0]
                print(sub_tag)
                content = sub_tag.find_next_sibling("p")
                cleaned = re.sub(r'[^a-zA-Z\s]', '', i)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                save_dict.update({cleaned.lower().replace(" ", "_"): content.text})
    return save_dict


final_dict = {}
urls = search("little women")
print(urls)
print(get_info(final_dict, list(urls)[0]))