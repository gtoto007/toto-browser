import socket
import ssl
from idlelib.rpc import response_queue


class URL_WEB:
    def __init__(self, url):

        if url.startswith("view-source:"):
            url = url.replace("view-source:", "")
            self.view_source = True
        else:
            self.view_source = False

        if "://" in url:
            self.scheme, url = url.split("://", 1)
        elif ":" in url:
            self.scheme, url = url.split(":", 1)
        else:
            raise ValueError("URL must contain a scheme")

        assert self.scheme in ["http", "https", "view-source"], "Unknown scheme"

        if "/" in url:
            self.host, self.path = url.split("/", 1)
            self.path = "/" + self.path
        else:
            self.host = url
            self.path = "/"

        if self.scheme == "https":
            self.port = 443
        elif self.scheme == "http":
            self.port = 80
        if ":" in self.host:
            self.host, self.port = self.host.split(":", 1)
            self.port = int(self.port)

    def request(self):
        if self.scheme == "file":
            return self.file_request()
        else:
            return self.web_request()

    def file_request(self):
        with open(self.path, "r") as f:
            return [], f.read()

    def web_request(self):
        request = f"GET {self.path} HTTP/1.1\r\n"

        headers = []
        headers.append(f"Host: {self.host}")
        headers.append("Connection: close")
        headers.append("User-Agent: TotoBrowser")

        request += "\r\n".join(headers) + "\r\n\r\n"

        s = self.create_socket(self.scheme, self.host, self.port)
        s.send(request.encode("utf-8"))
        response = s.makefile("r", encoding="utf8", newline="\r\n", errors="replace")
        line = response.readline()  #'HTTP/1.0 200 OK
        response_headers = {}
        while True:
            line = response.readline()
            if not line or line == "\r\n":
                break

            key, value = line.split(":", 1)
            response_headers[key.casefold()] = value.strip()

        content = response.read()
        s.close()
        return response_headers, content

    def create_socket(self, scheme, host, port):
        s = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        )
        if scheme == "https":
            cts = ssl.create_default_context()
            s = cts.wrap_socket(s, server_hostname=host)
        s.connect((host, port))
        return s

    def get_path(self):
        return self.path

    def get_host(self):
        return self.host

    def get_scheme(self):
        return self.scheme


class DATA_URL:
    def __init__(self, url):
        assert url.startswith("data:")  # e.g. "data:text/html,Hello world!"
        self.view_source = False
        self.type = url.split(":", 1)[1]
        self.type, self.body = self.type.split(",", 1)

    def request(self):
        return [], self.body


class URL:
    @staticmethod
    def build(url):
        if url.startswith("data:"):
            return DATA_URL(url)

        return URL_WEB(url)


def render(url):
    url = URL.build(url)
    headers, body = url.request()
    show(body, url.view_source)


def show(body, view_source):
    import re

    # Replace HTML entities with their corresponding characters
    body = body.replace("&lt;", "<")
    body = body.replace("&gt;", ">")

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
            print(c, end="")


if __name__ == "__main__":
    print("***Render https schema URL ***")
    render("https://browser.engineering/examples/example1-simple.html")

    print("***Render view-source Schema URL***")
    render("view-source:https://browser.engineering/examples/example1-simple.html")

    print("***Render Data schema URL ***")
    render("data:text/html,<h1>Hello world!</h1>")
