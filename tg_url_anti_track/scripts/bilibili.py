from urllib.parse import urlparse
from abv_py import bv2av

def process(url: str) -> str:
    parsed = urlparse(url)

    if not parsed.path.startswith("/video/"):
        return url

    if not parsed.path.lower().startswith("/video/bv"):
        return url

    bvid = parsed.path.split("/")[2]
    try:
        avid = f"av{bv2av(bvid)}"
        url = url.replace(bvid, avid)
    except:
        pass
    finally:
        return url
