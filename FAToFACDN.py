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
    """
    Checks PMs and comment scores and handles them if necessary
    """
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
            logging.debug("ID was: {0}, Comment Contents were:\n{1}\n Link for context: https://www.reddit.com{2}?context=5".format(bot_comment.id, bot_comment.body, bot_comment.permalink))
    check = 0


def allowed_to_reply(comment):
    """
    Checks whether the bot has replied to the comment before or if the user has blacklisted themselves
    :param comment: The comment we want to check
    :return: False if not allowed to reply, True otherwise
    """
    return not (comment.author.name + "\n" in open("Blacklist.txt", 'r').read() or comment.id+"\n" in open("Repliedto.txt", 'r'))


def source_exists(link, original):
    """
    Tries to find if the source exists in as many ways as possible
    :param link: the link we want to check
    :param original: the original post we're checking in
    :return: True if source exists, False otherwise
    """
    return (quote(link, safe="://") in quote(original, safe="://")) or (quote(link, safe="://") in original) or (link in original)  # Just to be safe...


def sort_tags(original_tag_order):
    """
     Sort all tags in the same way /u/furbot_ does
    :param original_tag_order: The tags in the order they were extracted in
    :return: The tag list sorted by priority
    """
    new_tag_order = []
    replace_list = [["ambiguous_gender", "male", "female", "intersex", "cuntboy", "dickgirl", "herm", "maleherm", "manly", "girly", "tomboy"], ["bondage", "domination", "submissive", "sadism", "masochism", "size_play", "hyper", "macro", "micro", "'pok\\xc3\\xa9mon'", "transformation", "cock_transformation", "gender_transformation", "post_transformation", "scat_transformation", "inflation", "belly_expansion", "cum_inflation", "scat_inflation", "vore", "soft_vore", "hard_vore", "absorption_vore", "soul_vore", "anal_vore", "auto_vore", "breast_vore", "nipple_vore", "cock_vore", "oral_vore", "tail_vore", "imminent_vore", "post_vore", "unbirthing", "cannibalism", "vore_sex", "scat", "watersports", "gore", "grotesque_death", "crush", "stomping", "snuff", "necrophilia", "ballbusting", "cock_and_ball_torture", "genital_mutilation", "rape", "abuse", "degradation", "forced", "gang_rape", "mind_break", "public_use", "questionable_consent", "assisted_rape", "oral_rape", "tentacle_rape", "armpit_fetish", "balloon_fetish", "fart_fetish", "foot_fetish", "hoof_fetish", "navel_fetish", "sock_fetish", "what", "why"], ["male/female", "male/male", "female/female", "intersex/male", "cuntboy/male", "dickgirl/male", "herm/male", "maleherm/male", "intersex/female", "cuntboy/female", "dickgirl/female", "herm/female", "maleherm/female", "intersex/intersex", "cuntboy/cuntboy", "dickgirl/cuntboy", "dickgirl/dickgirl", "dickgirl/herm", "herm/cuntboy", "herm/herm", "maleherm/cuntboy", "maleherm/dickgirl", "maleherm/herm", "maleherm/maleherm", "ambiguous/ambiguous", "male/ambiguous", "female/ambiguous", "intersex/ambiguous", "cuntboy/ambiguous", "dickgirl/ambiguous", "herm/ambiguous", "maleherm/ambiguous"], ["feral", "semi-anthro", "humanoid", "human", "taur"], ["penetration", "anal_penetration", "cloacal_penetration", "oral_penetration", "urethral_penetration", "vaginal_penetration", "cervical_penetration", "double_penetration", "double_anal", "double_vaginal", "triple_penetration", "triple_anal", "triple_vaginal", "oral", "cloacalingus", "cunnilingus", "collaborative_cunnilingus", "fellatio", "beakjob", "collaborative_fellatio", "deep_throat", "double_fellatio", "oral_knotting", "rimming", "deep_rimming", "snout_fuck", "sideways_oral", "tonguejob", "licking", "ball_lick", "penis_lick", "oral_masturbation", "autocunnilingus", "autofellatio", "auto_penis_lick", "autorimming", "autotonguejob", "fisting", "anal_fisting", "double_fisting", "urethral_fisting", "vaginal_fisting", "fingering", "anal_fingering", "clitoral_fingering", "cloacal_fingering", "vaginal_fingering", "urethral_fingering", "fingering_self", "fingering_partner", "frottage", "grinding", "hot dogging", "tailjob", "titfuck", "tribadism"], ["69_position", "amazon_position", "anvil_position", "arch_position", "chair_position", "cowgirl_position", "deck_chair_position", "from_behind_position", "leg_glider_position", "lotus_position", "mastery_position", "missionary_position", "piledriver_position", "prison_guard_position", "reverse_cowgirl_position", "reverse_piledriver_position", "reverse_missionary_position", "sandwich_position", "speed_bump_position", "spoon_position", "stand_and_carry_position", "t_square_position", "table_lotus_position", "totem_pole_position", "train_position", "triangle_position", "unusual_position", "wheelbarrow_position", "1691", "ass_to_ass", "daisy_chain", "doggystyle", "mating_press", "mounting", "polesitting", "reverse_spitroast", "spitroast"]]
    for tag_list in replace_list:
        for tag in original_tag_order:
            if tag in tag_list:
                new_tag_order.append(tag)
    for tag in original_tag_order:
        if tag not in new_tag_order:
            new_tag_order.append(tag)
    return new_tag_order


def tag_formatter(tags):
    """
    Formats each tag in the list so that reddit formatting doesn't screw it up
    :param tags:  The list of tags to format
    :return: A String of the tags formatted properly
    """
    formatted = []
    omitted_tags = len(tags) - 30
    tags = tags[:30]
    for tag in tags:
        word = ""
        for character in tag:
            if character in ['*', '~', '_', '^', '\\', '(', ')', '[', ']', '>']:
                character = '\\' + character
            word += character
        formatted.append(word)
    return_string = "^" + ' ^'.join(formatted)
    if omitted_tags > 0:
        return_string += " ^and ^{0} ^Omitted ^Tags".format(omitted_tags)
    return return_string


def not_duplicate(link_to_check, existing_posts):
    for post in existing_posts:
        if post.direct_link == link_to_check:
            return False
    return True


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
    logging.debug("Comment contents are: {0}\nLink is: https://www.reddit.com{1}?context=5".format(comment.body, comment.permalink))
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
                if not source_exists(link_info.direct_link[8:], comment_body) and not_duplicate(link_info.direct_link, posts):
                    posts.append(link_info)
                    sample_urls.append(link_info.sample_url)
                else:
                    logging.info("Source for that link already exists.")
            else:
                posts.append(link_info)
        for sample_url in sample_urls:
            if sample_url is not None:
                if source_exists(sample_url[8:], comment_body):
                    reply += "I've noticed you tried to add a direct link to your post, But you linked a lower resolution one, Please look at [this guide!](https://imgur.com/a/RpklH) to see how to properly add direct links to your post! \n\n"
                    break
        iterator = len(posts)
        index = 0
        while index < iterator:
            if not isinstance(posts[index], list):
                post = posts[index]
                try:
                    if post.download_file("images/image_{0}".format(index)):
                        logging.debug("Successfully downloaded image_{0}, File Size is: {1}KB".format(index, int(os.path.getsize("images/image_{0}.{1}".format(index, post.direct_link.split('.')[-1]))) / 1000))
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
                    reply += tag_formatter(sort_tags(post.tags))
                reply += "\n\n"
                index += 1
            else:
                post = posts[index]
                number = 0
                direct_links = []
                images = []
                for file in post:
                    if file.download_file("images/image_{0}_{1}".format(index, number)):
                        logging.debug("Successfully downloaded image_{0}_{1}, File Size is: {2}KB".format(index, number, int(os.path.getsize("images/image_{0}_{1}.{2}".format(index, number, file.direct_link.split('.')[-1]))) / 1000))
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
                    reply += tag_formatter(sort_tags(post[0].tags))
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