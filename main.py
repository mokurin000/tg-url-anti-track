import telegram
from telegram.ext import InlineQueryHandler, CommandHandler, Application, ContextTypes
from telegram import Update
import re
import requests
import toml

with open("config.toml", "r") as f:
    config = toml.load(f)


def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.bot.send_message(chat_id=update.message.chat_id, text="Hello! I'm a URL parser bot. Just type a URL and I "
                                                                  "will remove all the tracking parameters.")


def match_expand(text, regex, expand):
    if regex:
        return re.search(regex, text).expand(expand)

    return text


def process_url(url, rule, domain):
    action = rule.get("action", "direct")

    url_regex = rule.get("url_regex", "")
    url_expand = rule.get("url_expand", '\\1')

    url = match_expand(url, url_regex, url_expand)

    if action == "direct":
        return url
    elif action == "request":
        r = requests.get(url, allow_redirects=False)

        content_regex = rule.get("content_regex", "")
        content_expand = rule.get("content_expand", '\\1')  # use '\1' by default

        return re.search(content_regex, r.text).expand(content_expand)
    else:
        raise f"unexpected action '{action}' in domain '{domain}'"


def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.inlinequery.query
    url = re.search('https?(://[^ \n]*)', query, re.IGNORECASE)

    if not url:
        results = [
            telegram.InlineQueryResultArticle(
                id='1', title="no url found", input_message_content=telegram.InputTextMessageContent(
                    "no URL found in your query!\n你是故意来找茬的吧？"))
        ]
        context.bot.answer_inline_query(update.inlinequery.id, results)
        return

    url = url.expand("https\\1")  # ensure "http://b23.tv" will be converted to "https://..."
    domain = re.findall('://([a-zA-Z0-9._-]+)', url, re.IGNORECASE)[0]

    if domain not in config:
        results = [
            telegram.InlineQueryResultArticle(
                id='1', title="unsupported url", input_message_content=telegram.InputTextMessageContent(
                    "unsupported url.\n"
                    "please check [repo](https://github.com/poly000/tg-url-anti-track), create an issue/pr for support.", parse_mode="MarkdownV2"))
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
    app = Application.builder().token("YOUR_BOT_TOKEN").build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(InlineQueryHandler(inline_query))
    app.run_polling()


if __name__ == '__main__':
    main()
