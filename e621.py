from Py621 import getById
import re
import requests
import shutil
import logging
log = logging.getLogger(__name__)
log.info("e621.py has set up logging successfully")


class post_data:
    def __init__(self, direct_link, artist_name, tags, rating, sample_url):
        self.direct_link = direct_link
        self.artist_name = artist_name
        self.image_name = "None"
        self.tags = tags
        if rating == "e":
            self.rating = "Explicit"
        elif rating == "q":
            self.rating = "Questionable"
        elif rating == "s":
            self.rating = "Safe"
        else:
            self.rating = "Unknown"
        self.sample_url = sample_url[8:]
        log.debug("A post_data class was created with the following values: direct_link:{0}, artist_name:{1}, image_name:{2}, tags:{3}, rating:{4}, sample_url:{5}".format(self.direct_link, self.artist_name, self.image_name, self.tags, self.rating, self.sample_url))

    def download_file(self, name):
        user_agent = "Py621/1.1 (by Hidoni on e621)"
        try:
            image = requests.get(self.direct_link, stream=True, headers={'User-Agent': user_agent})
            name = name + '.' + self.direct_link.split('.')[-1]
            with open(name, 'wb') as output_location:
                image.raw.decode_content = True
                shutil.copyfileobj(image.raw, output_location)
            del image
            return True
        except Exception as e:
            log.debug("Got the following error while trying to download: {0}".format(str(e)))
            return False

def isolateID(e621_link):
    return re.findall(r"\d+", e621_link)[1]

def get_e621_info(e621_link):
    log.info("Now handling the following link: {0}".format(e621_link))
    post = getById(isolateID(e621_link=e621_link))
    if post is None:
        return "Can't mirror"
    elif post.file_ext in ["swf", "webm"]:
        return "Can't mirror"
    try: return post_data(post.file_url, post.artist, post.tags, post.rating, post.sample_url)
    except Exception as e:
        log.info("Got the following error while trying to mirror: " + str(e))
        return "Can't mirror"  # If something has gone wrong, Instead of crashing just ignore this link.
