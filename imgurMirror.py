from imgurpython import ImgurClient

clientid = "0209c87fabd7f2e"
clientsecret = "c93c3b0c06b062a4cf2d7dff1035d8d399c32afb"

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
