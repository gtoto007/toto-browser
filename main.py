from pprint import pprint
from idlelib.rpc import response_queue
from URLs.URL import URL

MAX_REDIRECTS = 4


def render(url, redirect_count=0):
    url = URL.build(url)
    headers, status, body = url.request()
    show(body, url.view_source)


def show(body, view_source):
    import re

    if view_source:
        print(body)
        return

    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif in_tag and c == "/":
            print("\n", end="")
        elif not in_tag and c != "\n":
            # Replace HTML entities with their corresponding characters
            if c == "&lt;":
                c = "<"
            elif c == "&gt;":
                c = ">"

            print(c, end="")


def main():
    import sys

    # Get URLs from command line arguments, use default if none provided
    # e.g. python browser.py "https://example.com" "data:text/html,<h1>Hello world!</h1>" "view-source:http://example.com"
    urls = (
        sys.argv[1:]
        if len(sys.argv) > 1
        else [
            "https://www.freesoft.org/CIE/Topics/4.htm",
            "https://www.freesoft.org/CIE/Topics/88.htm",
            "view-source:http://giuseppetoto.it",
        ]
    )

    for url in urls:
        # Handle quoted URLs by removing outer quotes if present
        if (url.startswith('"') and url.endswith('"')) or (
            url.startswith("'") and url.endswith("'")
        ):
            url = url[1:-1]

        print(f"\n--- Rendering {url} ---\n")
        render(url)


if __name__ == "__main__":
    main()
