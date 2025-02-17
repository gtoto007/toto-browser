import socket
import ssl
from idlelib.rpc import response_queue


class URL_WEB:
    # define a static dictionary to store the sockets for each single url
    sockets = {}

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
        headers.append("Connection: keep-alive")
        headers.append("User-Agent: TotoBrowser")

        request += "\r\n".join(headers) + "\r\n\r\n"
        socket = self.get_socket(self.scheme, self.host, self.port)
        socket.send(request.encode("utf-8"))
        response = socket.makefile(
            "rb", encoding="utf8", newline="\r\n", errors="replace"
        )
        line = response.readline().decode("utf-8")  #'HTTP/1.0 200 OK
        response_headers = {}
        while True:
            line = response.readline().decode("utf-8")
            if not line or line == "\r\n":
                break

            key, value = line.split(":", 1)
            response_headers[key.casefold()] = value.strip()

        content = response.read(int(response_headers.get("content-length", 0))).decode(
            "utf-8"
        )
        # socket.close()
        return response_headers, content

    def get_socket(self, scheme, host, port):
        if self.host not in URL_WEB.sockets:
            URL_WEB.sockets[self.host] = self.create_socket(
                self.scheme, self.host, self.port
            )
        return URL_WEB.sockets[self.host]

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
    urls = (
        sys.argv[1:]
        if len(sys.argv) > 1
        else [
            "https://www.freesoft.org/CIE/Topics/4.htm",
            "https://www.freesoft.org/CIE/Topics/88.htm",
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
