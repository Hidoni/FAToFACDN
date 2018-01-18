from imgurpython import ImgurClient
import json
from urllib.parse import quote
import logging
log = logging.getLogger(__name__)
log.info("imgurMirror.py has set up logging successfully")

# Get the credentials for the imgur account
creds = json.load(open("imgur.json"))
clientid = creds["clientid"]
clientsecret = creds["clientsecret"]

client = ImgurClient(clientid, clientsecret)

def mirrorImage(path, name):
    log.info("imgurMirror.py now mirroring the following link: " + path)
    config = {
        'album': None,
        'name': name,
        'title': name,
        'description': 'This image is a mirror of a FurAffinity Image linked on a reddit post.'
    }
    image = client.upload_from_url(url=quote(path, safe="://"), config=config, anon=False)
    return image['link']
