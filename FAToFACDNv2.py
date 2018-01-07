import praw
from praw.models import Message
from bs4 import BeautifulSoup
import re
from time import sleep
import logging
import cfscrape
import json
import imgurMirror
from e621Link import getInfo

reddit = praw.Reddit('bot') # the bot's info is part of praw.ini allowing it to be added easily
subreddit = reddit.subreddit("furry_irl") # Makes praw only grab info related to furry_irl

# Setting up Console & File logging:

logger = logging.getLogger('FAToFACDN')
handler = logging.FileHandler('FAToFACDN.log', encoding='utf_8')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s') # Format is Time, log level(debug, info, etc..), log message
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG) # Log everything to the file
console = logging.StreamHandler()
console.setLevel(logging.INFO) # Log everything except debug messages to the console
console.setFormatter(formatter)
logger.addHandler(console)

reply = "You've linked images from e621/FurAffinity without direct links, Here are those links!\n\n" # Base reply
name = [] # Some lists that will store names, links, keywords etc.
keywords = []
list = []
artist = []
FALinks = []
CDNLinks = []
source = False
index = -1 # A counter to delete things from lists by indexing if necessary
check = 0 # A counter to check PMs only after a certain amount of messages
cookies = json.load(open('cookie.json')) # Since FA uses recaptcha on login, It's much easier to use their login cookies that don't expire for an entire year.
scraper = cfscrape.create_scraper() # Since FA added cloudflare to their site and still does not have an API, We need to use the module 'cfscrape' that bypasses cloudflare's anti bot protection page
default_FA_Link = "http://www.furaffinity.net"
default_IMG_Link = "www.furaffinity.net/view/"

def cleanString(string): # A Function to strip links of their brackets if they have reddit formatting
    end = string.index(")")
    return string[:end]
def getFACDNLink(FALink):
    logging.info("Getting FACDN Link for: " + FALink)
    list = [] # Reset the list since it may be filled with info from previous function calls
    scraper.get(default_FA_Link) # Make a GET request to the landing page of FA so that we get basic cookies from the site
    scraper.cookies.update(cookies) # Update cookies so that we are logged in, allowing the bot to view mature/adult images.
    HTML = scraper.get(FALink).content # Get the page and store its HTML content to a variable
    soup = BeautifulSoup(HTML, 'html.parser')
    part = soup.find('img', {'id':'submissionImg'})
    for data in soup.find_all('div', attrs={'id','keywords'}): # Find the div that has the keywords
        for a in data.find_all('a'): # Get all a hrefs
            list.append(a.contents[0]) # Append their content, Basically the keyword
    keywords.append(list) # Append the list of the keywords to the entire list
    try: link = part["data-fullview-src"] # Store the link in a variable
    except TypeError: return "Can't mirror"
    imgname = part["alt"] # FA uses the alt tag to store the image name in case the image fails to load, so we'll put that in it's own variable
    art = soup.findAll('a',href=re.compile("^/user/")) # Find all the a href tags that lead to a users page
    art = art[1] # Get the second one, since the first one is the bot's username
    art = art.contents[0] # Get the contents of the tag, which is the artists name
    art = [art]
    name.append(imgname)
    artist.append(art)
    global index
    index += 1
    return "https://"+link[2:]
def performCheck():
    logger.info("Reading PMs and checking comment scores")
    for message in reddit.inbox.unread(limit=None):
        if isinstance(message, Message): # If it's a message
            logger.info("Found PM from User: " + message.author.name)
            if message.subject == "Blacklist": # And it's title is Blacklist, It's automatically the title if the user clicks on the "Blacklist yourself" at the bottom of the bots replys
                logger.info("They want to be blacklisted from the bot, adding their name to the list")
                with open("Blacklist.txt", 'a') as f:
                    f.write(message.author.name + "\n")
                    logger.debug("Added user " + message.author.name + " To Blacklist.txt")
                message.reply("Ok, I will no longer reply to your posts.")
        message.mark_read()
    for botcmt in reddit.user.me().comments.new(limit=None):
        if botcmt.score < -2: # If the score is lower than negative two delete it.
            botcmt.delete()
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
def sourceExist(FACDNLink, part):
    if FACDNLink in part:
        return True
    return False
# Main comment stream
for comment in subreddit.stream.comments():
    # Reset some variables
    reply = "You've linked images from e621/FurAffinity without direct links, Here are those links!\n\n"
    name = []
    keywords = []
    artist = []
    FALinks = []
    CDNLinks = []
    source = False
    index = -1
    check += 1
    if check > 9:
        performCheck()
        check = 0
    logger.info("Now viewing comment with id: " + comment.id)
    logger.debug("Comment contents are: " + comment.body)
    logger.debug("Comment link is: https://www.reddit.com" + comment.permalink + "?context=5")
    body = comment.body.replace("full","view")
    body = body.replace("e926","e621")
    splitcmt = re.findall(r'(furaffinity.net/view/\S+)', body)
    splitcmt += re.findall(r'(e621.net/post/show/\S+)', body)
    if allowedToReply(comment):
        for part in splitcmt:
                logger.debug("Now parsing the following part: \"" + part + "\" from comment: " + comment.id)
                if "furaffinity.net/view/" in part:
                    if ")" in part:
                        FALink = "https://www." + cleanString(part)
                    else:
                        FALink = "https://www." + part
                    FACDNLink = getFACDNLink(FALink)
                    if FACDNLink == "Can't mirror":
                        logger.info("It's a swf or webm, Can't mirror it!")
                        continue
                    source = sourceExist(FACDNLink[8:], body)
                    if not source:
                        logger.info("Adding {0} to FALinks and {1} to CDNLinks".format(FALink, FACDNLink))
                        FALinks.append(FALink)
                        CDNLinks.append(FACDNLink)
                    else:
                        logger.info("They already provided the source, removing existing info about post")
                        del artist[index]
                        del keywords[index]
                        del name[index]
                        index -= 1
                else:
                    esixlink = getInfo(part)
                    if esixlink == "Can't mirror":
                        logger.info("It's a swf or webm, Can't mirror it!")
                        continue
                    source = sourceExist(esixlink.direct_link, body)
                    if not source:
                        logger.info("Adding {0} to FALinks and {1} to CDNLinks and {2} to artists and {3} to keywords".format(part, esixlink.direct_link, esixlink.artist_name, esixlink.tags))
                        FALinks.append(part)
                        CDNLinks.append(esixlink.direct_link)
                        artist.append(esixlink.artist_name)
                        keywords.append(esixlink.tags)
                        name.append(esixlink.image_name)
                        index += 1
                    else:
                        logger.info("They already provided the source.")
        for x in range(0, len(FALinks)):
            reply += "[Link]({0}) | Image Name: {1} | Artist: {2} | [Imgur Mirror]({3})\n\n ^Tags: ".format(CDNLinks[x], name[x], (', '.join(['%s']*len(artist[x])) % tuple(artist[x])), imgurMirror.uploadImage(CDNLinks[x],name[x]))
            if len(keywords[x]) == 0:
                reply += "^None"
            else:
                for y in keywords[x]:
                    reply += "^" + y + " "
            reply += "\n\n"
        reply += "***\n^^Bot ^^Created ^^By ^^Hidoni, ^^Have ^^I ^^made ^^an ^^error? [^^Message ^^creator](https://www.reddit.com/message/compose/?to=Hidoni&subject=Bot%20Error) ^^| [^^Blacklist ^^yourself](https://www.reddit.com/message/compose/?to=FAToFacdn&subject=Blacklist) ^^| ^^If ^^this ^^comment ^^goes ^^below ^^-2 ^^karma, ^^It ^^will ^^be ^^deleted" # Final line in the reply
        if (len(FALinks) > 0): # If there are actually any links in the comment
            with open("Repliedto.txt",'a') as f:
                f.write(comment.id + "\n")
            comment.reply(reply)
            logger.info("replied to comment with id: "+comment.id)
            logger.debug("Reply message was:\n"+reply)
            sleep(2)
    else:
        logger.info("I've either already replied to this comment or the user wanted to be blacklisted, So I won't be replying.")
