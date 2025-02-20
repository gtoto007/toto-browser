from URLs.DATA_URL import DATA_URL
from URLs.WEB_URL import WEB_URL


class URL:
    @staticmethod
    def build(url):
        if url.startswith("data:"):
            return DATA_URL(url)

        return WEB_URL(url)
