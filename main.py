import praw
import logging

logger = None
reddit = praw.Reddit('bot')
subreddit = reddit.subreddit("furry_irl")


def setup_logging():
    file = logging.FileHandler("FAToFACDN.log", encoding="utf-8")
    console = logging.StreamHandler()
    console.setLevel("INFO")
    logging.basicConfig(format="{asctime:s} {name:s}-{levelname:s} {message:s}", style='{', handlers=[file, console], level=logging.DEBUG)
    global logger
    logger = logging.getLogger("main")


if __name__ == '__main__':
    setup_logging()
