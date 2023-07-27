from urllib.parse import urlparse
from avbv import bv2av

def process(url: str) -> str:
    parsed = urlparse(url)

    if not parsed.path.startswith("/video/"):
        return url

    if not parsed.path.lower().startswith("/video/bv"):
        return url

    bvid = parsed.path.split("/")[2]
    avid = bv2av(bvid)

    return url.replace(bvid, avid)

