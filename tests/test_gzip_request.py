import json
from URLs.WEB_URL import WEB_URL


def test_gzip_requet():

    browser = WEB_URL("https://httpbin.org/gzip")
    headers, status, content = browser.request()
    obj = json.loads(content)
    assert status == 200
    assert headers["content-encoding"] == "gzip"
    assert obj["gzipped"] == True
