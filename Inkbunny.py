import re
import requests
import json
import shutil
import logging
log = logging.getLogger(__name__)
log.info("Inkbunny.py has set up logging successfully")

credentials = json.load(open("Inkbunny.json"))
username = credentials["username"]
password = credentials["password"]

session_id = json.loads(requests.get("https://inkbunny.net/api_login.php?username={0}&password={1}".format(username, password)).content)["sid"]  # Get a session ID

class post_data:
    def __init__(self, direct_link, artist_name, image_name, tags, rating):
        self.direct_link = direct_link
        self.artist_name = [artist_name]
        self.image_name = image_name
        self.tags = tags[0:30]
        self.rating = rating
        self.sample_url = None
        log.debug("A post_data class was created with the following values: direct_link:{0}, artist_name:{1}, image_name:{2}, tags:{3}, rating:{4}".format(self.direct_link, self.artist_name, self.image_name, self.tags, self.rating))

    def download_file(self, name):
        try:
            image = requests.get(self.direct_link, stream=True)
            name = name + '.' + self.direct_link.split('.')[-1]
            with open(name, 'wb') as output_location:
                image.raw.decode_content = True
                shutil.copyfileobj(image.raw, output_location)
            del image
            return True
        except Exception as e:
            log.debug("Got the following error while trying to download: {0}".format(str(e)))
            return False

def get_new_session_id():
    global session_id
    session_id = json.loads(requests.get("https://inkbunny.net/api_login.php?username={0}&password={1}".format(username, password)).content)["sid"]

def isolateID(inkbunny_link):
    return re.findall(r"\d+", inkbunny_link)[0]

def get_submission(submission_id):
    global session_id
    return json.loads(requests.get("https://inkbunny.net/api_submissions.php?sid={0}&submission_ids=[{1}]".format(session_id, submission_id)).content)

def get_inkbunny_info(inkbunny_link):
    log.info("Now handling the following link: {0}".format(inkbunny_link))
    json_result = get_submission(isolateID(inkbunny_link))
    submission = json_result["submissions"][0]
    try:
        if int(submission["error_code"]) == 2:
            get_new_session_id()
            json_result = get_submission(isolateID(inkbunny_link))
            submission = json_result["submissions"][0]
        else:
            return "Can't mirror"
    except:
        pass
    direct_links = []
    artist_name = submission["username"]
    image_name = submission["title"]
    tags = []
    if submission["type_name"] in ["Shockwave/Flash - Interactive", "Video - Feature Length", "Music - Single Track", "Music - Album", "Writing - Document"]:
        return "Can't mirror"
    elif "swf" in submission["file_url_full"] or "mp4" in submission["file_url_full"] or "webm" in submission["file_url_full"]:
        return "Can't mirror"
    rating = submission["rating_name"]
    for keyword in submission["keywords"]:
        tags.append(keyword["keyword_name"].replace(' ', '_'))
    for image in submission["files"]:
        direct_links.append(image["file_url_full"])
    images = []
    for link in direct_links:
        images.append(post_data(link, artist_name, image_name, tags, rating))
    if len(images) > 1:
        return images
    return images[0]
