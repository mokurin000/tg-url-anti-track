import telegram
from telegram.ext import InlineQueryHandler, CommandHandler, Application, ContextTypes
from telegram import Update

import re
import toml

import requests

from urllib.parse import urlparse, parse_qs

with open("config.toml", "r") as f:
    config = toml.load(f)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id, text="Hello! I'm a URL parser bot.\n"
                                                                        "Just type a URL in inline query,"
                                                                        "and I will remove all the tracking "
                                                                        "parameters.")


def match_expand(text, regex, expand):
    if regex:
        return re.search(regex, text).expand(expand)

    return text


def process_url(url, rule, domain):
    action = rule.get("action", "")

    if not action:
        raise "{domain}: action must not be empty!"

    match action:
        case "direct":
            parsed = urlparse(url)
            reversed_params = rule.get("params", [])
            params = parse_qs(parsed.query)

            scheme = parsed.scheme
            netloc = parsed.netloc
            path = parsed.path if parsed.path else "/"
            url = f"{scheme}://{netloc}{path}?"

            for param in reversed_params:
                url += f"&{param}={params[param]}"

            return url.replace("?&", "?")
        case "request":
            ctx = requests.get(url, allow_redirects=False).text
        case "redirect":
            ctx = requests.get(url, allow_redirects=False).headers["Location"]
        case _:
            raise f"unexpected action '{action}' in domain '{domain}'"

    content_regex = rule.get("content_regex", "")
    content_expand = rule.get("content_expand", '\\1')

    url = re.search(content_regex, ctx).expand(content_expand)
    domain = urlparse(url).netloc
    return process_url(url, {"action": "direct"}, domain)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    url = re.search('https?(://[^ \n，。]*)', query, re.IGNORECASE)

    if not url:
        results = [
            telegram.InlineQueryResultArticle(
                id='1', title="no url found", input_message_content=telegram.InputTextMessageContent(
                    "no URL found in your query!\n"
                    "你是故意来找茬的吧？"))
        ]
        await context.bot.answer_inline_query(update.inline_query.id, results)
        return

    url = url.expand("https\\1")  # ensure "http://b23.tv" will be converted to "https://..."
    domain = urlparse(url).netloc

    if domain not in config:
        results = [
            telegram.InlineQueryResultArticle(
                id='1', title="unsupported url", input_message_content=telegram.InputTextMessageContent(
                    "unsupported url.\n"
                    "please check [repo](https://github.com/poly000/tg-url-anti-track),"
                    " create an issue/pr for support.", parse_mode="MarkdownV2"))
        ]
        await context.bot.answer_inline_query(update.inline_query.id, results)
        return

    rule = config[domain]
    url = process_url(url, rule, domain)

    results = [
        telegram.InlineQueryResultArticle(
            id='1', title="URL", input_message_content=telegram.InputTextMessageContent(url))
    ]

    await context.bot.answer_inline_query(update.inline_query.id, results)


def main():
    app = Application.builder().token("YOUR_BOT_TOKEN").build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(InlineQueryHandler(inline_query))
    app.run_polling()


if __name__ == '__main__':
    main()
