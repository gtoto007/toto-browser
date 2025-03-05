import tkinter
import random
import math

from URLs.URL import URL

WIDTH, HEIGHT = 800, 600


def random_color():
    """Generate a random color in hex format."""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"#{r:02x}{g:02x}{b:02x}"


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("Toto Browser")
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)

        self.canvas.pack()
        self.window.focus_force()

    def load(self, url):
        url = URL.build(url)
        headers, status, content = url.request()
        text = self.lex(content)[:200]
        self.canvas.create_text(
            20,
            20,
            text=text,
            font=("Helvetica", 12),
            fill="black",
            anchor=tkinter.NW,  # Anchor the text to the north (top)
        )
        self.window.mainloop()

    def lex(self, content):
        import re

        in_tag = False
        text = ""
        for c in content:
            if c == "<":
                in_tag = True
            elif c == ">":
                in_tag = False
            elif in_tag and c == "/":
                text += "\n"
            elif not in_tag and c != "\n":
                # Replace HTML entities with their corresponding characters
                if c == "&lt;":
                    text += "<"
                elif c == "&gt;":
                    text += ">"

                text += c
        return text


if __name__ == "__main__":
    browser = Browser()
    browser.load("https://giuseppetoto.it/what-story-point-actually-is-bddd403504db")
