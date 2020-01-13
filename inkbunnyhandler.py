import re
import requests
import json
import shutil
import logging

logger = logging.getLogger(__name__)

credentials = json.load(open("inkbunny.json"))
username = credentials["username"]
password = credentials["password"]

session_id = json.loads(requests.get(f"https://inkbunny.net/api_login.php?username={username}&password={password}").content)["sid"]  # Get a session ID


class InkBunnyInfo:
    def __init__(self, direct_link, artist, image_name, tags, rating):
        self.direct_link = direct_link
        self.artist = [artist]
        self.image_name = image_name
        self.tags = tags
        self.rating = rating
        self.sample_url = None
        logger.debug(f"Info class created with the following values: direct_link:{direct_link}, artist_name:{artist}, tags:{tags}, rating:{rating}")

    @staticmethod
    def _download_single(path, url):
        try:
            image = requests.get(url, stream=True)
            name = path + '.' + url.split('.')[-1]
            with open(name, 'wb') as output_location:
                image.raw.decode_content = True
                shutil.copyfileobj(image.raw, output_location)
            del image
            return name
        except Exception as e:
            logger.debug("Got the following error while trying to download: {0}".format(str(e)))
            return None

    def download(self, path):
        if isinstance(self.direct_link, list):
            images = []
            for x in range(len(self.direct_link)):
                images.append(self._download_single(f"{path}_{x}", self.direct_link[x]))
            return images
        else:
            return self._download_single(path, self.direct_link)


def get_new_session_id():
    global session_id
    session_id = json.loads(requests.get(f"https://inkbunny.net/api_login.php?username={username}&password={password}").content)["sid"]


def request_post(post_id):
    return json.loads(requests.get(f"https://inkbunny.net/api_submissions.php?sid={session_id}&submission_ids=[{post_id}]").content)


def get(link):
    logger.info(f"Handling URL: {link}")
    json_result = request_post(re.findall(r"\d+", link)[0])
    submission = json_result["submissions"][0]
    try:
        if int(submission["error_code"]) == 2:
            get_new_session_id()
            json_result = request_post(re.findall(r"\d+", link)[0])
            submission = json_result["submission"][0]
        else:
            return None
    except:  # No error.
        pass
    direct_links = []
    artist = submission["username"]
    image_name = submission["title"]
    tags = []
    if submission["type_name"] in ["Shockwave/Flash - Interactive", "Video - Feature Length", "Music - Single Track", "Music - Album", "Writing - Document"] or "swf" in submission["file_url_full"] or "mp4" in submission["file_url_full"] or "webm" in submission["file_url_full"]:
        return None
    rating = submission["rating_name"]
    for keyword in submission["keywords"]:
        tags.append(keyword["keyword_name"].replace(' ', '_'))
    for image in submission["files"]:
        direct_links.append(image["file_url_full"])
    if len(direct_links) == 1:
        direct_links = direct_links[0]
    return InkBunnyInfo(direct_links, artist, image_name, tags, rating)
