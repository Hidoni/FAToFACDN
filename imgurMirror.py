from imgurpython import ImgurClient
import json

creds = json.load(open("imgur.json"))
clientid = creds["clientid"]
clientsecret = creds["clientsecret"]

client = ImgurClient(clientid, clientsecret)

def uploadImage(path, name):
    config = {
        'album': None,
        'name': name,
        'title': name,
        'description': 'This image is a mirror of a FurAffinity Image linked on a reddit post.'
    }
    image = client.upload_from_url(url=path, config=config, anon=False)
    return image['link']
