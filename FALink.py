import cfscrape
from bs4 import BeautifulSoup
import re
import json
import logging
log = logging.getLogger(__name__)
log.info("FALink.py has set up logging successfully")

login_info = json.load(open('cookie.json'))
scraper = cfscrape.create_scraper()


class postData():
    def __init__(self, direct_link, artist_name, image_name, tags, rating, sample_url):
        self.direct_link = "https://" + direct_link[2:]
        self.artist_name = artist_name
        self.image_name = image_name
        self.tags = tags[0:30]
        self.rating = rating
        self.sample_url = sample_url[2:]
        log.debug("A postData class was created with the following values: direct_link:{0}, artist_name:{1}, image_name:{2}, tags:{3}, rating:{4}".format(self.direct_link, self.artist_name, self.image_name, self.tags, self.rating))


def getFAInfo(FALink):
    keywordList = []
    log.info("FALink.py is now handling the following link: " + FALink)
    scraper.get("http://www.furaffinity.net")  # Make a request to the landing page of FA
    scraper.cookies.update(login_info)  # Update our session's cookies to log into FA without passing a captcha
    HTML = scraper.get(FALink).content  # Get the HTML content of the image
    soup = BeautifulSoup(HTML, 'html.parser')  # Parse it using BeautifulSoup 4
    subImg = soup.find('img', id="submissionImg")  # Find the part of the page that contains the actual image
    if soup.find('div', class_="audio-player-container"):  # If there's an audio container that means it's an audio file which means mirroring would be useless
        return "Can't mirror"
    try: direct_link=subImg["data-fullview-src"]
    except TypeError: return "Can't mirror"
    for data in soup.find_all('div', id="keywords"):
        for a in data.find_all('a'):
            keywordList.append(a.contents[0])
    imame_name = subImg["alt"]
    art = soup.findAll('a', href=re.compile("^/user/"))
    art = art[1].contents[0]
    artist_name = [art]
    if soup.find("img", alt="Adult rating"):
        rating = "Explicit"
    elif soup.find("img", alt="Mature rating"):
        rating = "Questionable"
    elif soup.find("img", alt="General rating"):
        rating = "Safe"
    else:
        rating = "Unknown"
    sample_url = subImg["data-preview-src"]
    return postData(direct_link, artist_name, imame_name, keywordList, rating, sample_url)
