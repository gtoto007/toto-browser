import unittest
from browser import render


class TestMain(unittest.TestCase):
    def test_render(self):
        self.assertIsNone(render("https://example.com"))
        self.assertIsNone(render("data:text/html,<h1>Hello world!</h1>"))
        self.assertIsNone(render("view-source:http://example.com"))


if __name__ == "__main__":
    unittest.main()
