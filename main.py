import telegram
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.ext import _applicationbuilder
import re
import requests
import toml

with open("config.toml", "r") as f:
    config = toml.load(f)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Hello! I'm a URL parser bot. Just type a URL and I "
                                                                  "will remove all the tracking parameters.")


def match_expand(text, regex, expand):
    if regex:
        return re.search(regex, text).expand(expand)

    return text


def process_url(url, rule, domain):
    action = rule.get("action", "direct")

    url_regex = rule.get("url_regex", "")
    url_expand = rule.get("url_expand", '\1')

    url = match_expand(url, url_regex, url_expand)

    if action == "direct":
        return url
    elif action == "request":
        r = requests.get(url)

        content_regex = rule.get("content_regex", "")
        content_expand = rule.get("content_expand", '\1') # use '\1' by default

        return re.search(content_regex, r.text).expand(content_expand)
    else:
        raise f"unexpected action '{action}' in domain '{domain}'"


def inline_query(update, context):

    query = update.inlinequery.query
    url = re.search('https?://[^ \n]*', query, re.IGNORECASE)

    if not url:
        results = [
            telegram.InlineQueryResultArticle(
                id='1', title="no url found", input_message_content=telegram.InputTextMessageContent("no URL found in your query!\n你是故意来找茬的吧？"))
        ]
        context.bot.answer_inline_query(update.inlinequery.id, results)
        return

    url = url[0]
    domain = re.findall('://([a-zA-Z0-9._-]+)', url, re.IGNORECASE)[0]

    if domain not in config:
        results = [
            telegram.InlineQueryResultArticle(
                id='1', title="unsupported url", input_message_content=telegram.InputTextMessageContent("unsupported url.\nplease check at [repo](https://github.com/poly000/tg-url-anti-track)")).parse_mode
        ]
        context.bot.answer_inline_query(update.inlinequery.id, results)
        return

    rule = config[domain]
    url = process_url(url, rule, domain)

    results = [
        telegram.InlineQueryResultArticle(
            id='1', title="URL", input_message_content=telegram.InputTextMessageContent(url))
    ]

    context.bot.answer_inline_query(update.inlinequery.id, results)


def main():
    updater = Updater('YOUR_API_KEY')

    dp = DispatcherBuilder
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(InlineQueryHandler(inline_query))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
