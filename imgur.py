import pyimgur
import requests
import json
import logging

logger = logging.getLogger(__name__)

credentials = json.load(open("imgur.json"))
client = pyimgur.Imgur(credentials['client_id'])


def create_album(images, name):
    payload = [('title', name)]
    for image in images:
        payload.append(('deletehashes[]', image))
    headers = {'Authorization': f"Client-ID {credentials['client_id']}"}
    return f'https://imgur.com/a/{json.loads(requests.post("https://api.imgur.com/3/album", payload, headers=headers).content)["data"]["id"]}'


def mirror(images, name):
    if images is None:
        raise Exception("Can't mirror none")
    if isinstance(images, list):
        logger.info("Mirroring multiple images and creating an album")
        uploaded = []
        for image in images:
            uploaded.append(client.upload_image(image, title=name, description="This image is a mirror of a an image linked on a furry_irl post or sent to /u/fatofacdn in dms."))
        deletehashes = [x.deletehash for x in uploaded]
        logger.debug(f"List of deletehashes: {deletehashes}")
        return create_album(deletehashes, name)
    logger.info("Mirroring a single image")
    uploaded = client.upload_image(images, title=name, description="This image is a mirror of a an image linked on a furry_irl post or sent to /u/fatofacdn in dms.")
    logger.debug(f"Deletehash: {uploaded.deletehash}")
    return uploaded.link
