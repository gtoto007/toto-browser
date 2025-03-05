import unittest
from URLs.WEB_URL import WEB_URL
from main import render
from Cache import Cache


class TestMain(unittest.TestCase):
    def test_render(self):
        self.assertIsNone(render("https://example.com"))
        self.assertIsNone(render("data:text/html,<h1>Hello world!</h1>"))
        self.assertIsNone(render("view-source:http://example.com"))

    def test_cache_request(self):
        cache = Cache()
        cache.reset()
        url = "https://static.anonymised.io/light/retargeting.js"
        browser = WEB_URL(url)
        browser.request()
        self.assertTrue(cache.has_valid_cache(url))


if __name__ == "__main__":
    unittest.main()
