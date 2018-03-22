from imgurpython import ImgurClient
import json
import logging
log = logging.getLogger(__name__)
log.info("imgurMirror.py has set up logging successfully")

# Get the credentials for the imgur account
credentials = json.load(open("imgur.json"))
client_id = credentials["client_id"]
client_secret = credentials["client_secret"]

client = ImgurClient(client_id, client_secret)


def mirror_image(path, name):
    config = {
        'album': None,
        'name': name,
        'title': name,
        'description': 'This image is a mirror of a an image linked on a furry_irl post.'
    }
    image = client.upload_from_path(path=path, config=config, anon=False)
    log.info("Mirrored the image successfully, Link is {0}".format(image['link']))
    return image['link']
