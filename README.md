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

## Ruleset format

```toml
["domain1"]
# direct if need no request
#
# if a domain was not found in ruleset, it will use 'direct' action
# without any param.
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
# Optional, specify a general params for all matched urls from this short url
r_params = ["id"]

["domain3"]
# redirect when it returns 301 redirect
action = "redirect"
# Optional, specify a general params for all matched urls from this short url
r_params = ["id"]

```
