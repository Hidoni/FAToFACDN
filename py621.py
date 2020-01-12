import requests
import json
import time
import datetime

user_agent = "Py621/1.2 (by Hidoni on e621)"
last_request = datetime.datetime.min
base_link = "https://e621.net/post/"
host = "e621.net"


class e621Post:
    def __init__(self, id, author, creator_id, created_at, status, source, tags, artist, description, fav_count, score,
                 rating, parent_id, has_children, children, has_notes, md5, file_url, file_ext, file_size, width,
                 height, sample_url, sample_width, sample_height, preview_url, preview_width, preview_height):
        self.id = id
        self.author = author
        self.creator_id = creator_id
        self.created_at = created_at
        self.status = status
        self.source = source
        self.tags = tags
        self.artist = artist
        self.description = description
        self.fav_count = fav_count
        self.score = score
        self.rating = rating
        self.parent_id = parent_id
        self.has_children = has_children
        self.children = children
        self.has_notes = has_notes
        self.md5 = md5
        self.file_url = file_url
        self.file_ext = file_ext
        self.file_size = file_size
        self.width = width
        self.height = height
        self.sample_url = sample_url
        self.sample_width = sample_width
        self.sample_height = sample_height
        self.preview_url = preview_url
        self.preview_width = preview_width
        self.preview_height = preview_height


def handle_sleep():
    time_passed = datetime.datetime.now() - last_request
    if time_passed.total_seconds() < 1:
        time.sleep(1 - time_passed.total_seconds())


def get_page(request_url):
    handle_sleep()
    return requests.get(request_url, headers={'User-Agent': user_agent})


def get_top_of_week():
    posts = []
    req = get_page("https://e621.net/post/popular_by_week.json")
    JSON = json.loads(req.content.decode())
    for post in JSON:
        try:
            data = (e621Post(id=post['id'], tags=post['tags'].split(), description=post['description'],
                             created_at=post['created_at'], creator_id=post['creator_id'], author=post['author'],
                             source=post['sources'], score=post['score'], fav_count=post['fav_count'], md5=post['md5'],
                             file_size=post['file_size'], file_url=post['file_url'], file_ext=post['file_ext'],
                             preview_url=post['preview_url'], preview_width=post['preview_width'],
                             preview_height=post['preview_height'], sample_url=post['sample_url'],
                             sample_width=post['sample_width'], sample_height=post['sample_height'],
                             rating=post['rating'], status=post['status'], width=post['width'], height=post['height'],
                             has_notes=post['has_notes'], has_children=post['has_children'], children=post['children'],
                             parent_id=post['parent_id'], artist=post['artist']))
        except KeyError:
            data = (e621Post(id=post['id'], tags=post['tags'].split(), description=post['description'],
                             created_at=post['created_at'], creator_id=post['creator_id'], author=post['author'],
                             source=post['source'], score=post['score'], fav_count=post['fav_count'], md5=post['md5'],
                             file_size=post['file_size'], file_url=post['file_url'], file_ext=post['file_ext'],
                             preview_url=post['preview_url'], preview_width=post['preview_width'],
                             preview_height=post['preview_height'], sample_url=post['sample_url'],
                             sample_width=post['sample_width'], sample_height=post['sample_height'],
                             rating=post['rating'], status=post['status'], width=post['width'], height=post['height'],
                             has_notes=post['has_notes'], has_children=post['has_children'], children=post['children'],
                             parent_id=post['parent_id'], artist=post['artist']))
        posts.append(data)
    return posts


def search_by_tags(Tags):
    posts = []
    req = get_page("https://e621.net/post/index.json?tags={0}&limit=100".format(Tags))
    JSON = json.loads(req.content.decode())
    for post in JSON:
        try:
            data = (e621Post(id=post['id'], tags=post['tags'].split(), description=post['description'],
                             created_at=post['created_at'], creator_id=post['creator_id'], author=post['author'],
                             source=post['sources'], score=post['score'], fav_count=post['fav_count'], md5=post['md5'],
                             file_size=post['file_size'], file_url=post['file_url'], file_ext=post['file_ext'],
                             preview_url=post['preview_url'], preview_width=post['preview_width'],
                             preview_height=post['preview_height'], sample_url=post['sample_url'],
                             sample_width=post['sample_width'], sample_height=post['sample_height'],
                             rating=post['rating'], status=post['status'], width=post['width'], height=post['height'],
                             has_notes=post['has_notes'], has_children=post['has_children'], children=post['children'],
                             parent_id=post['parent_id'], artist=post['artist']))
        except KeyError:
            data = (e621Post(id=post['id'], tags=post['tags'].split(), description=post['description'],
                             created_at=post['created_at'], creator_id=post['creator_id'], author=post['author'],
                             source=post['source'], score=post['score'], fav_count=post['fav_count'], md5=post['md5'],
                             file_size=post['file_size'], file_url=post['file_url'], file_ext=post['file_ext'],
                             preview_url=post['preview_url'], preview_width=post['preview_width'],
                             preview_height=post['preview_height'], sample_url=post['sample_url'],
                             sample_width=post['sample_width'], sample_height=post['sample_height'],
                             rating=post['rating'], status=post['status'], width=post['width'], height=post['height'],
                             has_notes=post['has_notes'], has_children=post['has_children'], children=post['children'],
                             parent_id=post['parent_id'], artist=post['artist']))
        posts.append(data)
    return posts


def get_by_id(id):
    req = get_page("https://e621.net/post/show.json?id={0}".format(id))
    post = json.loads(req.content.decode())
    if post["status"] == "deleted":
        return None
    try:
        data = (e621Post(id=post['id'], tags=post['tags'].split(), description=post['description'],
                         created_at=post['created_at'], creator_id=post['creator_id'], author=post['author'],
                         source=post['sources'], score=post['score'], fav_count=post['fav_count'], md5=post['md5'],
                         file_size=post['file_size'], file_url=post['file_url'], file_ext=post['file_ext'],
                         preview_url=post['preview_url'], preview_width=post['preview_width'],
                         preview_height=post['preview_height'], sample_url=post['sample_url'],
                         sample_width=post['sample_width'], sample_height=post['sample_height'], rating=post['rating'],
                         status=post['status'], width=post['width'], height=post['height'], has_notes=post['has_notes'],
                         has_children=post['has_children'], children=post['children'], parent_id=post['parent_id'],
                         artist=post['artist']))
    except KeyError:
        data = (e621Post(id=post['id'], tags=post['tags'].split(), description=post['description'],
                         created_at=post['created_at'], creator_id=post['creator_id'], author=post['author'],
                         source=post['source'], score=post['score'], fav_count=post['fav_count'], md5=post['md5'],
                         file_size=post['file_size'], file_url=post['file_url'], file_ext=post['file_ext'],
                         preview_url=post['preview_url'], preview_width=post['preview_width'],
                         preview_height=post['preview_height'], sample_url=post['sample_url'],
                         sample_width=post['sample_width'], sample_height=post['sample_height'], rating=post['rating'],
                         status=post['status'], width=post['width'], height=post['height'], has_notes=post['has_notes'],
                         has_children=post['has_children'], children=post['children'], parent_id=post['parent_id'],
                         artist=post['artist']))
    return data
