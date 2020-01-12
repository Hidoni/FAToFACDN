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
    return requests.post("https://api.imgur.com/3/album", payload, headers=headers)


def mirror(images, name):
    if isinstance(images, list):
        uploaded = []
        for image in images:
            uploaded.append(client.upload_image(image, title=name, description="This image is a mirror of a an image linked on a furry_irl post or sent to /u/fatofacdn in dms."))
        return client.create_album(name, images=[x.deletehash for x in uploaded]).link
    return client.upload_image(images, title=name, description="This image is a mirror of a an image linked on a furry_irl post or sent to /u/fatofacdn in dms.").link
