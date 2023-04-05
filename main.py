import telegram
from telegram.ext import InlineQueryHandler, CommandHandler, Application, ContextTypes
from telegram import Update

import re
import toml

import requests

from urllib.parse import urlparse, parse_qs

with open("rules.toml", "r") as f:
    ruleset = toml.load(f)

with open("config.toml", "r") as f:
    config = toml.load(f)

default_rule = {"action": "direct"}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id, text="Hello! I'm a URL parser bot.\n"
                                                                        "Just type a URL in inline query,\n"
                                                                        "and I will remove all the tracking "
                                                                        "parameters.")


def match_expand(text, regex, expand):
    if regex:
        return re.search(regex, text).expand(expand)

    return text


def clean_param(url, reversed_params):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    scheme, netloc = parsed.scheme, parsed.netloc

    path = parsed.path if parsed.path else "/"
    url = f"{scheme}://{netloc}{path}?"

    for param in reversed_params:
        if param in params:
            url += f"&{param}={params[param][0]}"

    url = url.replace("?&", "?")  # if no param was matched

    return url.removesuffix("?")


def process_url(url, rule, domain):
    action = rule.get("action", "direct")

    match action:
        case "direct":
            reversed_params = rule.get("params", [])
            return clean_param(url, reversed_params)
        case "request":
            ctx = requests.get(url, allow_redirects=False).text
        case "redirect":
            ctx = requests.get(url, allow_redirects=False).headers["Location"]
        case "regex":
            url_regex = rule.get("url_regex", "")
            url_expand = rule.get("url_expand", "\\1")

            return re.search(url_regex, url).expand(url_expand)
        case _:
            raise f"unexpected action '{action}' in domain '{domain}'"

    content_regex = rule.get("content_regex", "")
    content_expand = rule.get("content_expand", '\\1')

    url = re.search(content_regex, ctx).expand(content_expand)
    domain = urlparse(url).netloc

    r_params = rule.get("r_params", None)

    if r_params:
        return clean_param(url, r_params)

    return process_url(url, ruleset.get(domain, default_rule), domain)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    url = re.search('http(s?)(://[^ \n，。]*)', query, re.IGNORECASE)

    if not url:
        no_url_found = [
            telegram.InlineQueryResultArticle(
                id='1', title="no url found", input_message_content=telegram.InputTextMessageContent(
                    "no URL found in your query!\n"
                    "你是故意来找茬的吧？"))
        ]
        await context.bot.answer_inline_query(update.inline_query.id, no_url_found)
        return

    origin_url = url.expand("http\\1\\2")
    url = url.expand("https\\2")  # ensure "http://b23.tv" will be converted to "https://..."
    domain = urlparse(url).netloc

    rule = ruleset.get(domain, default_rule)
    url = process_url(url, rule, domain)

    processed_url = [
        telegram.InlineQueryResultArticle(
            id='1', title="cleaned URL",
            input_message_content=telegram.InputTextMessageContent(url)),
        telegram.InlineQueryResultArticle(
            id='2', title="cleaned message",
            input_message_content=telegram.InputTextMessageContent(query.replace(origin_url, url))
        )
    ]

    await context.bot.answer_inline_query(update.inline_query.id, processed_url)


def main():
    api_token = config.get("bot_token", "YOUR_BOT_TOKEN")
    app = Application.builder().token(api_token).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(InlineQueryHandler(inline_query))
    app.run_polling()


if __name__ == '__main__':
    main()
