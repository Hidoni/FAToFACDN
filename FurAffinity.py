import cfscrape
from bs4 import BeautifulSoup
import re
import json
import shutil
import logging
log = logging.getLogger(__name__)
log.info("FurAffinity.py has set up logging successfully")

login_info = json.load(open('cookie.json'))
scraper = cfscrape.create_scraper()


class post_data:
    def __init__(self, direct_link, artist_name, image_name, tags, rating, sample_url):
        self.direct_link = "https://" + direct_link[2:]
        self.artist_name = artist_name
        self.image_name = image_name
        self.tags = tags
        self.rating = rating
        self.sample_url = sample_url[2:]
        log.debug("A post_data class was created with the following values: direct_link:{0}, artist_name:{1}, image_name:{2}, tags:{3}, rating:{4}".format(self.direct_link, self.artist_name, self.image_name, self.tags, self.rating))

    def download_file(self, name):
        try:
            image = scraper.get(self.direct_link, stream=True)
            name = name + '.' + self.direct_link.split('.')[-1]
            with open(name, 'wb') as output_location:
                image.raw.decode_content = True
                shutil.copyfileobj(image.raw, output_location)
            del image
            return True
        except Exception as e:
            log.debug("Got the following error while trying to download: {0}".format(str(e)))
            return False

def get_furaffinity_info(furaffinity_link):
    keyword_list = []
    log.info("Now handling the following link: " + furaffinity_link)
    scraper.get("http://www.furaffinity.net")  # Make a request to the landing page of FA
    scraper.cookies.update(login_info)  # Update our session's cookies to log into FA without passing a captcha
    html = scraper.get(furaffinity_link).content  # Get the html content of the image
    soup = BeautifulSoup(html, 'html.parser')  # Parse it using BeautifulSoup 4
    submission_img = soup.find('img', id="submissionImg")  # Find the part of the page that contains the actual image
    if soup.find('div', class_="audio-player-container"):  # If there's an audio container that means it's an audio file which means mirroring would be useless
        return "Can't mirror"
    if soup.find('div', class_="font-size-panel"):  # This div only appears on story posts.
        return "Can't mirror"
    try: direct_link = submission_img["data-fullview-src"]
    except TypeError: return "Can't mirror"
    for data in soup.find_all('div', id="keywords"):
        for a in data.find_all('a'):
            keyword_list.append(a.contents[0])
    image_name = submission_img["alt"]
    art = soup.findAll('a', href=re.compile("^/user/"))
    artist_name = re.findall(r"^/user/(\w+)", art[1]['href'])
    if soup.find("img", alt="Adult rating"):
        rating = "Explicit"
    elif soup.find("img", alt="Mature rating"):
        rating = "Questionable"
    elif soup.find("img", alt="General rating"):
        rating = "Safe"
    else:
        rating = "Unknown"
    sample_url = submission_img["data-preview-src"]
    return post_data(direct_link, artist_name, image_name, keyword_list, rating, sample_url)