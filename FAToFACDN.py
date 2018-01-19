import praw
from praw.models import Message
import re
from time import sleep
import logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level="DEBUG", handlers=[logging.FileHandler("FAToFACDN.log", encoding="utf-8")]) # Sets up logging to both console and a file
console = logging.StreamHandler()
console.setLevel("INFO")
console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logging.getLogger("").addHandler(console)
logging.info("FAToFACDN.py has set up logging successfully")
from e621Link import getESixInfo
from FALink import getFAInfo
from imgurMirror import mirrorImage
from urllib.parse import quote

reddit = praw.Reddit('bot') # the bot's info is part of praw.ini allowing it to be added easily
subreddit = reddit.subreddit("furry_irl") # Makes praw only grab info related to furry_irl

def performCheck():
    logging.info("Reading PMs and checking comment scores")
    for message in reddit.inbox.unread(limit=None):
        if isinstance(message, Message):
            logging.info("Found PM From user: " + message.author.name)
            if message.subject == "Blacklist":
                logging.info("They want to be blacklisted to the bot, adding their name to the list...")
                with open("Blacklist.txt", 'a') as f:
                    f.write(message.author.name + "\n")
                    logging.info("Added user: " + message.author.name + " To Blacklist.txt")
                message.reply("Ok, I will no longer reply to your comments.")
        message.mark_read()
    for botcmt in reddit.user.me().comments.new(limit=None):
        if botcmt.score < 0:
            botcmt.delete()
def cleanString(string):
    end = string.index(")")
    return string[:end]
def allowedToReply(comment):
    with open("Blacklist.txt",'r') as f:
        file = f.readlines()
        for name in file:
            if name == comment.author.name + "\n":
                return False
    with open("Repliedto.txt",'r') as f:
        file = f.readlines()
        for id in file:
            if id == comment.id+"\n":
                return False
    return True
def sourceExists(link, original):
    if (quote(link, safe="://") in quote(original, safe="://")) or (quote(link, safe="://") in original):
        return True
    return False
check = 0
for comment in subreddit.stream.comments():
    reply = "You've linked images from e621/FurAffinity without direct links, Here are those links!\n\n"
    direct_links = []
    artist_names = []
    image_names = []
    tags_list = []
    image_ratings = []
    index = -1
    check += 1
    if (check == 10):
        performCheck()
        check = 0
    logging.info("Now viewing comment with id: {0}, Made by {1}".format(comment.id, comment.author.name))
    logging.debug("Comment contents are: {0}\nLink is https://www.reddit.com{1}?context=5".format(comment.body, comment.permalink))
    body = comment.body.replace("full","view") # Replace any instance of the word full with the word view, so we can parse FA links easier
    body = body.replace("e926","e621") # Same thing as above, just for e621 links
    splitcmt = re.findall(r'(furaffinity.net/view/\S+)', body) # using re to find all FA and e621 links in the comment
    splitcmt += re.findall(r'(e621.net/post/show/\S+)', body)
    if allowedToReply(comment):
        for part in splitcmt:
            logging.debug("Now parsing the following part: {0}, from comment: {1}".format(part, comment.id))
            if "furaffinity.net/view/" in part:
                if ")" in part:
                    FALink = "https://www." + cleanString(part)
                else:
                    FALink = "https://www." + part
                link_info = getFAInfo(FALink)
                if link_info == "Can't mirror":
                    logging.info("It's a swf/webm, Can't mirror")
                    continue
            else:
                if ")" in part:
                    esixlink = "https://www." + cleanString(part)
                else:
                    esixlink = "https://www." + part
                link_info = getESixInfo(esixlink)
                if link_info == "Can't mirror":
                    logging.info("It's a swf/webm, Can't mirror")
                    continue
            if not sourceExists(link_info.direct_link[8:], body):
                        direct_links.append(link_info.direct_link)
                        artist_names.append(link_info.artist_name)
                        image_names.append(link_info.image_name)
                        tags_list.append(link_info.tags)
                        image_ratings.append(link_info.rating)
                        index += 1
            else:
                logging.info("Source for that link already exists.")
        for x in range(0, len(direct_links)):
            try:
                reply += "[Link]({0}) | Image Name: {1} | Artist: {2} | Rating: {4} | [Imgur Mirror]({3})\n\n ^Tags: ".format(direct_links[x], image_names[x], (', '.join(['%s']*len(artist_names[x])) % tuple(artist_names[x])), mirrorImage(direct_links[x],image_names[x]), image_ratings[x])
                sleep(1)
            except Exception as e: 
                logging.info("Ran into the following error while trying to add another part to the reply: " + str(e))
                del direct_links[x]
                continue
            if len(tags_list[x]) == 0:
                reply += "^None"
            else:
                for y in tags_list[x]:
                    reply += "^" + y + " "
            reply += "\n\n"
        reply += "***\n^^Bot ^^Created ^^By ^^Hidoni, ^^Have ^^I ^^made ^^an ^^error? [^^Message ^^creator](https://www.reddit.com/message/compose/?to=Hidoni&subject=Bot%20Error) ^^| [^^Blacklist ^^yourself](https://www.reddit.com/message/compose/?to=FAToFacdn&subject=Blacklist) ^^| ^^If ^^this ^^comment ^^goes ^^below ^^0 ^^karma, ^^It ^^will ^^be ^^deleted"
        if len(direct_links) > 0:
            with open("Repliedto.txt", 'a') as f:
                f.write(comment.id + "\n")
            comment.reply(reply)
            logging.info("Replied to comment with id: " + comment.id)
            logging.debug("Reply message was:\n"+reply)
            sleep(2)
    else:
        logging.info("I've either already replied to this comment or the user wanted to be blacklisted, So I won't be replying.")
