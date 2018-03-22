import praw
from praw.models import Message
import re
import logging
from urllib.parse import quote
import os
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level="DEBUG", handlers=[logging.FileHandler("FAToFACDN.log", encoding="utf-8")])  # Sets up logging to both console and a file
console = logging.StreamHandler()
console.setLevel("INFO")
console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logging.getLogger("").addHandler(console)
logging.info("FAToFACDN.py has set up logging successfully")
from e621 import get_e621_info
from FurAffinity import get_furaffinity_info
from Inkbunny import get_inkbunny_info
from imgur import mirror_image

reddit = praw.Reddit('bot')
subreddit = reddit.subreddit('furry_irl')

def perform_check():
    global check
    logging.info("Checking PMs and Comment Scores")
    for message in reddit.inbox.unread():
        if isinstance(message, Message):
            if message.subject == "Blacklist":
                logging.info("Found a blacklist request from {0}".format(message.author.name))
                with open("Blacklist.txt", 'a') as f:
                    f.write(message.author.name + "\n")
                    logging.debug("Added user: " + message.author.name + " To Blacklist.txt")
                message.reply("Ok, I will no longer reply to your comments.")
        message.mark_read()
    for bot_comment in reddit.user.me().comments.new(limit=20):
        if bot_comment.score < 0:
            bot_comment.delete()
            logging.info("Found a comment with a score below 0, It has been deleted")
            logging.debug("ID was: {0}, Comment Contents were:\n{1}".format(bot_comment.id, bot_comment.body))
    check = 0

def allowed_to_reply(comment):
    with open("Blacklist.txt", 'r') as f:
        file = f.readlines()
        for name in file:
            if name == comment.author.name + "\n":
                return False
    with open("Repliedto.txt", 'r') as f:
        file = f.readlines()
        for id in file:
            if id == comment.id+"\n":
                return False
    return True

def sourceExists(link, original):
    return (quote(link, safe="://") in quote(original, safe="://")) or (quote(link, safe="://") in original) or (link in original)  # Just to be safe...

def tagFormatter(tags):
    formatted = []
    for tag in tags:
        word = ""
        for character in tag:
            if character in ['*', '~', '_', '^', '\\', '(', ')', '[', ']', '>']:
                character = '\\' + character
            word += character
        formatted.append(word)
    return "^" + ' ^'.join(formatted)

check = 0
for comment in subreddit.stream.comments():
    check += 1
    if "You've linked images from e621/FurAffinity/Inkbunny without direct links".lower() in comment.body.lower():
        reply = "Hey, That's my line!\n\n"
    else:
        reply = "You've linked images from e621/FurAffinity/Inkbunny without direct links, Here are those links!\n\n"
    posts = []
    sample_urls = []
    if check == 10:
        perform_check()
    logging.info("Checking comment with ID: {0}, By: {1}".format(comment.id, comment.author.name))
    logging.debug("Comment contents are: {0}\nLink is: {1}".format(comment.body, comment.permalink))
    comment_body = comment.body.replace("e926.net", "e621.net")
    comment_body = comment_body.replace("full", "view")
    urls_to_mirror = re.findall(r"(furaffinity\.net/view/\d+)", comment_body)  # Match all FurAffinity urls
    urls_to_mirror += re.findall(r"(e621\.net/post/show/\d+)", comment_body)  # Match all e621 urls
    urls_to_mirror += re.findall(r"(inkbunny\.net/s/\d+)", comment_body)  # Match all inkbunny urls
    if allowed_to_reply(comment):
        for url in urls_to_mirror:
            logging.debug("Now parsing the following part of the comment: {0}".format(url))
            if "furaffinity.net" in url:
                link_info = get_furaffinity_info("https://www." + url)
                if link_info == "Can't mirror":
                    logging.info("It's a swf/webm/audio file, Can't mirror")
                    continue
            elif "e621.net" in url:
                link_info = get_e621_info("https://www." + url)
                if link_info == "Can't mirror":
                    logging.info("It's a swf/webm/audio file, Can't mirror")
                    continue
            else:
                link_info = get_inkbunny_info("https://www." + url)
                if link_info == "Can't mirror":
                    logging.info("It's a swf/webm/audio file, Can't mirror")
                    continue
            if not isinstance(link_info, list):
                if not sourceExists(link_info.direct_link, comment_body):
                    posts.append(link_info)
                    sample_urls.append(link_info.sample_url)
                else:
                    logging.info("Source for that link already exists.")
            else:
                posts.append(link_info)
        for sample_url in sample_urls:
            if sample_url is not None:
                if sourceExists(sample_url, comment_body):
                    reply += "I've noticed you tried to add a direct link to your post, But you linked a lower resolution one, Please look at [this guide!](https://imgur.com/a/RpklH) to see how to properly add direct links to your post! \n\n"
                    break
        iterator = len(posts)
        index = 0
        while index < iterator:
            if not isinstance(posts[index], list):
                post = posts[index]
                try:
                    if post.download_file("images/image_{0}".format(index)):
                        reply += "[Link]({0}) | Image Name: {1} | Artist: {2} | Rating: {4} | [Imgur Mirror]({3})\n\n ^Tags: ".format(post.direct_link, post.image_name, (', '.join(['%s']*len(post.artist_name)) % tuple(post.artist_name)), mirror_image("images/image_{0}".format(str(index) + '.' + post.direct_link.split('.')[-1]), post.image_name), post.rating)
                        try: os.remove("images/image_{0}".format(str(index) + '.' + post.direct_link.split('.')[-1]))
                        except: pass
                    else:
                        logging.info("Failed to upload image...")
                        del posts[index]
                        iterator -= 1
                        try: os.remove("images/image_{0}".format(str(index) + '.' + post.direct_link.split('.')[-1]))
                        except: pass
                        continue
                except Exception as e:
                    logging.info("Ran into the following error while trying to add another part to the reply: {0}".format(str(e)))
                    del posts[index]
                    iterator -= 1
                    try: os.remove("images/image_{0}".format(str(index) + '.' + post.direct_link.split('.')[-1]))
                    except: pass
                    continue
                if len(post.tags) == 0:
                    reply += "^None"
                else:
                    reply += tagFormatter(post.tags)
                reply += "\n\n"
                index += 1
            else:
                post = posts[index]
                number = 0
                direct_links = []
                images = []
                for file in post:
                    if file.download_file("images/image_{0}_{1}".format(index, number)):
                        try:
                            images.append(mirror_image("images/image_{0}_{1}".format(index, str(number) + '.' + file.direct_link.split('.')[-1]), file.image_name))
                            direct_links.append(file.direct_link)
                            os.remove("images/image_{0}_{1}".format(index, str(number) + '.' + file.direct_link.split('.')[-1]))
                            number += 1
                        except:
                            os.remove("images/image_{0}_{1}".format(index, str(number) + '.' + file.direct_link.split('.')[-1]))
                links = ["[Link {0}]({1})".format(list(range(len(direct_links)))[x] + 1, direct_links[x]) for x in range(len(direct_links))]
                image_links = ["[Mirror {0}]({1})".format(list(range(len(images)))[x] + 1, images[x]) for x in range(len(images))]
                reply += "{0}| Image Name: {1} | Artist: {2} | Rating: {4} | {3}\n\n ^Tags: ".format(', '.join(links), post[0].image_name, (', '.join(['%s']*len(post[0].artist_name)) % tuple(post[0].artist_name)), ', '.join(image_links), post[0].rating)
                if len(post[0].tags) == 0:
                    reply += "^None"
                else:
                    reply += tagFormatter(post[0].tags)
                reply += "\n\n"
                index += 1
        reply += "***\n^^Bot ^^Created ^^By ^^Hidoni, ^^Have ^^I ^^made ^^an ^^error? [^^Message ^^creator](https://www.reddit.com/message/compose/?to=Hidoni&subject=Bot%20Error) ^^| [^^Blacklist ^^yourself](https://www.reddit.com/message/compose/?to=FAToFacdn&subject=Blacklist&message=Hi,%20I%20want%20to%20be%20blacklisted) ^^| [^^How ^^to ^^properly ^^give ^^direct ^^links](https://imgur.com/a/RpklH) ^^| ^^If ^^this ^^comment ^^goes ^^below ^^0 ^^karma, ^^It ^^will ^^be ^^deleted"
        if len(posts) > 0:
            with open("Repliedto.txt", 'a') as f:
                f.write(comment.id + "\n")
            comment.reply(reply)
            logging.info("Replied to comment with id: " + comment.id)
            logging.debug("Reply message was:\n"+reply)
    else:
        logging.info("I've either already replied to this comment or the user wanted to be blacklisted, So I won't be replying.")