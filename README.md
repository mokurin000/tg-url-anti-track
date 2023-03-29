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
["domain1"]
# direct if need no request
action = "direct"
# only 'id=xxx' will be reserved.
# if `params` is not set, drop all parameters.
params = ["id"] 

["domain2"]
# request for those like 'm.tb.cn'
action = "request"
# Required when action is 'request', default will noop
context_regex = "..." 
# Optional, default is "\1"
context_expand = "..." 

["domain3"]
# redirect when it returns 301 redirect
action = "redirect"

```
