import telegram
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import re
import requests
import toml

with open("config.toml", "r") as f:
    config = toml.load(f)

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Hello! I'm a URL parser bot. Just type a URL and I will remove all the tracking parameters.")

def replace_query_params(query, rule):
    url_regex = rule.get("url_regex", "")
    url_replace = rule.get("url_replace", "")

    if url_regex:
        return re.sub(url_regex, url_replace, query)
    else:
        return query

def process_url(url, rule):

    action = rule.get("action", "direct")

    if action == "direct":
        return replace_query_params(url, rule)
    elif action == "request":
        url = replace_query_params(url, rule)
        r = requests.get(url)

        content_regex = rule.get("content_regex", "")
        
        # use \1 by default
        content_expand = rule.get("content_expand", "\\1")

        if content_regex:
            return re.search(content_regex, r.text).expand(content_expand)
        else:
            return r.text

def inlinequery(update, context):

    query = update.inline_query.query

    if query:
        url = query

        domain = re.findall('://([a-zA-Z0-9._-]+)', url, re.IGNORECASE)[0]

        if domain not in config:
            results = [
                telegram.InlineQueryResultArticle(
                    id='1', title="unsupported url", input_message_content=telegram.InputTextMessageContent("unsupported url.\nplease check at repohttps://github.com/poly000/tg-url-anti-track"))
            ]
            context.bot.answer_inline_query(update.inline_query.id, results)
            return
        rule = config[domain]
        url = process_url(url, rule)

        results = [
            telegram.InlineQueryResultArticle(
                id='1', title="URL", input_message_content=telegram.InputTextMessageContent(url))
        ]

        context.bot.answer_inline_query(update.inline_query.id, results)

def main():
    updater = Updater('YOUR_API_KEY', use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(InlineQueryHandler(inlinequery))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

