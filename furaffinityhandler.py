import cfscrape
from bs4 import BeautifulSoup
import shutil
import re
import json
import logging

logger = logging.getLogger(__name__)

login_info = json.load(open("cookie.json"))
scraper = cfscrape.create_scraper()


class FurAffinityData:
    def __init__(self, direct_link, artist, image_name, tags, rating, sample_url):
        self.direct_link = "https://" + direct_link[2:]
        self.artist = [artist]
        self.image_name = image_name
        self.tags = tags
        self.rating = rating
        self.sample_url = sample_url[2:]
        logger.debug(f"Info class created with the following values: direct_link:{direct_link}, artist_name:{artist}, tags:{tags}, rating:{rating}, sample_url:{sample_url}")

    def download(self, path):
        try:
            image = scraper.get(self.direct_link, stream=True)
            name = path + '.' + self.direct_link.split('.')[-1]
            with open(name, 'wb') as output_location:
                image.raw.decode_content = True
                shutil.copyfileobj(image.raw, output_location)
            del image
            return name
        except Exception as e:
            logger.debug("Got the following error while trying to download: {0}".format(str(e)))
            return None


def get(link):
    logger.info(f"Handling URL: {link}")
    scraper.get("https://www.furaffinity.net/")  # I don't remember why exactly but this was required.
    scraper.cookies.update(login_info)
    html = scraper.get(link).content
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('div', class_="audio-player-container") or soup.find('div', class_="font-size-panel"):
        logger.info("URL Is actually an audio or story post.")
        return None
    submission_data = soup.find('img', id="submissionImg")
    try:
        direct_link = submission_data['data-fullview-src']
    except TypeError:
        logger.info("Submission is of an unknown type.")
        return None  # Some other type with no image, i.e. SWF
    image_name = submission_data['alt']
    for link in soup.findAll('a', href=re.compile("^/user/")):
        if link.find('img', class_="submission-user-icon floatleft avatar"):
            artist = re.match(r"/user/(\S+)/", link["href"]).groups()[0]
            break
    else:
        logger.debug("Failed to find artist name")
        return None  # Couldn't find artist
    rating = soup.find('span', class_="rating-box").get_text()
    sample_url = submission_data["data-preview-src"]
    tags = [tag.get_text() for tag in soup.find_all('span', class_="tags")]
    try:
        return FurAffinityData(direct_link, artist, image_name, tags, rating, sample_url)
    except Exception as e:
        logger.debug(f"Ran into the following exception when creating an FurAffinityInfo class: {e}")
        return None
