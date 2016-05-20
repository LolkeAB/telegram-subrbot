#!/usr/bin/env python
# This program is dedicated to the public domain under the CC0 license.
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
import logging
import praw
import html
from uuid import uuid4
from config import *
import re

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

reddit = praw.Reddit(user_agent=USER_AGENT)

def inlinequery(bot, update):
    query = update.inline_query.query

    res = list()
    
    if len(query) < 3: 
        bot.answerInlineQuery(update.inline_query.id, results=res)
        return

    print(query)
    subreddit = None

    try: 
        subreddit = reddit.get_subreddit(query)
        subreddit.fullname
    except:
        logger.warning('invalid subreddit: %s' % query)
        bot.answerInlineQuery(update.inline_query.id, results=res)
        return

    submissions = subreddit.get_hot(limit=25)

    for sub in submissions:
        offset = sub.name
        link_url = sub.url

        try:
            if 'imgur' in sub.url:
                m = re.search('imgur.com\/(\w*)', sub.url)
                link_url = 'https://i.imgur.com/' + m.group(1) + '.jpg'
        except:
            # voor het geval dat
            pass

        message = '<strong>{title}</strong> \n <a href="{url}">link</a> | <a href="https://www.reddit.com/r/{subreddit}">/r/{subreddit}</a> | <a href="{link}">permalink</a>'.format(title=html.escape(sub.title), url=html.escape(link_url), subreddit=sub.subreddit, link=sub.permalink)

        qwe = InlineQueryResultArticle(
            id=uuid4(),
            title=sub.title,
            input_message_content=InputTextMessageContent(message, parse_mode=ParseMode.HTML)
            )

        thumbnail = ''

        if hasattr(sub, 'preview'): 
            thumbnail = sub.preview['images'][0]['source']['url']
        
        try:
            if sub.secure_media != None:
                thumbnail = sub.secure_media['oembed']['thumbnail_url']
        except:
            # jammer
            pass

        qwe.thumb_url = thumbnail
        res.append(qwe)

    bot.answerInlineQuery(update.inline_query.id, results=res, cache_time=CACHE_TIME)

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.addHandler(InlineQueryHandler(inlinequery))


    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
