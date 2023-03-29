# tg-url-anti-track

Generated via [freegpt](https://freegpt.one)

## Installation

```bash
poetry install
```

## Usage

```bash
python main.py
```

## Todo

- [ ] use urllib.parse.{urlparse, parse_qs} instead of `url_regex`

## Config format

```toml
["domain"]
# direct if need no request
# request if need request with `allow_redirects=False`
action = "..."

url_regex = "..." # Optional
url_expand = "..." # Optional, default is "\1"

context_regex = "..." # Required when action is 'request', default will be noop
context_expand = "..." # Optional, default is "\1"

```
