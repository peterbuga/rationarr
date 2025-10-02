from furl import furl


def build_url(host, path="", query=None):
    url = furl(str(host)).add(path=path).add(args=(query or {})).url

    return url
