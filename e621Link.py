import esto # Conveniently enough, Someone made a really good module to interact with e621, making this much easier than it would've been otherwise.

class postData():
    def __init__(self, direct_link, artist_name, tags):
        self.direct_link = direct_link
        self.artist_name = artist_name
        self.image_name = "None"
        self.tags = tags[0:30]
def isolateID(e6link):
    e6link = e6link[19:]
    end = e6link.find("/")
    e6link = e6link[:end]
    return e6link
def getInfo(e6link):
    e6id = isolateID(e6link)
    post = esto.resolveid(e6id)
    if post.file_ext == "swf" or post.file_ext == "webm":
        return "Can't mirror"
    return postData(post.file_url, post.artists, post.tags)
