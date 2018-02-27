from Py621 import getById
import re
import logging
log = logging.getLogger(__name__)
log.info("e621Link.py has set up logging successfully")


class postData():
    def __init__(self, direct_link, artist_name, tags, rating, sample_url):
        self.direct_link = direct_link
        self.artist_name = artist_name
        self.image_name = "None"
        self.tags = tags[0:30]
        if rating == "e":
            self.rating = "Explicit"
        elif rating == "q":
            self.rating = "Questionable"
        elif rating == "s":
            self.rating = "Safe"
        else:
            self.rating = "Unknown"
        self.sample_url = sample_url[8:]
        log.debug("A postData class was created with the following values: direct_link:{0}, artist_name:{1}, image_name:{2}, tags:{3}, rating:{4}, sample_url:{5}".format(self.direct_link, self.artist_name, self.image_name, self.tags, self.rating, self.sample_url))


def isolateID(esixlink):
    esixid = re.findall('\d+', esixlink)
    return esixid[1]  # This returns the second value because the first one would be the 621 in e621.net


def getESixInfo(esixlink):
    log.info("e621Link.py is now handling the following link: " + esixlink)
    esixid = isolateID(esixlink)
    post = getById(esixid)
    if post == None: # This means that we tried to resolve a deleted post.
        return "Can't mirror"
    if post.file_ext == "swf" or post.file_ext == "webm":
        return "Can't mirror"  # Since imgur can't mirror swf or webm, and linking either of these would not allow it to be viewed, this string is returned which causes the bot to skip to the next link
    try: return postData(post.file_url, post.artist, post.tags, post.rating, post.sample_url)
    except Exception as e:
        log.info("Got the following error while trying to mirror: " + str(e))
        return "Can't mirror"  # If something has gone wrong, Instead of crashing just ignore this link.
