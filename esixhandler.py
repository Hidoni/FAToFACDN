import requests
import logging
import re
import py621
import shutil

logger = logging.getLogger(__name__)
RATING_MAP = {'e': "Explicit", 'q': "Questionable", 's': "Safe"}


class e621Info:
    def __init__(self, direct_link, artist, tags, rating, sample_url):
        self.direct_link = direct_link
        self.artist = artist
        self.image_name = None
        self.tags = tags
        try:
            self.rating = RATING_MAP[rating]
        except KeyError:
            self.rating = "Unknown"
        if direct_link != sample_url:
            self.sample_url = direct_link
        else:
            self.sample_url = None
        logger.debug(f"Info class created with the following values: direct_link:{direct_link}, artist_name:{artist}, tags:{tags}, rating:{rating}, sample_url:{self.sample_url}")

    def download(self, path):
        user_agent = "Py621/1.2 (by Hidoni on e621)"
        try:
            image = requests.get(self.direct_link, stream=True, headers={'User-Agent': user_agent})
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
    post_id = re.findall(r"\d+", link)[1]  # e*621*.net/post/*id* which is why we take the second match
    post = py621.get_by_id(post_id)
    if post is None or post.file_ext in ["swf", "webm"]:
        logger.info("Could not mirror")
        return None
    try:
        return e621Info(post.file_url, post.artist, post.tags, post.rating, post.sample_url)
    except Exception as e:
        logger.debug(f"Ran into the following exception when creating an e621Info class: {e}")
        return None
