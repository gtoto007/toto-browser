import socket
import ssl
from cache_browser import CacheBrowser


class WEB_URL:
    # define a static dictionary to store the sockets for each single url
    sockets = {}

    def __init__(self, url):

        self.original_url = url

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
            return self._file_request()
        else:
            return self._web_request()

    def _file_request(self):
        with open(self.path, "r") as f:
            return [], 200, f.read()

    def _web_request(self):
        cache = CacheBrowser()
        if cache.has_valid_cache(self.host):
            headers, content = cache.get_cached_file(self.host)
            return headers, 200, content

        request = f"GET {self.path} HTTP/1.1\r\n"

        headers = []
        headers.append(f"Host: {self.host}")
        headers.append("Connection: keep-alive")
        headers.append("User-Agent: TotoBrowser")

        request += "\r\n".join(headers) + "\r\n\r\n"
        socket = self._get_socket(self.scheme, self.host, self.port)
        socket.send(request.encode("utf-8"))
        response = socket.makefile(
            "rb", encoding="utf8", newline="\r\n", errors="replace"
        )
        line = response.readline().decode("utf-8")  #'HTTP/1.0 200 OK
        version, status, explanation = line.split(" ", 2)
        status = int(status)
        response_headers = {}
        while True:
            line = response.readline().decode("utf-8")
            if not line or line == "\r\n":
                break

            key, value = line.split(":", 1)
            response_headers[key.casefold()] = value.strip()

        content = response.read(int(response_headers.get("content-length", 0)))

        if "max-age" in response_headers.get("cache-control", ""):
            cache.save_to_cache(self.original_url, content, response_headers)

        if isinstance(content, str):
            content = content.encode("utf-8")

        return response_headers, status, content

    def _is_socket_valid(self, sock):
        try:
            # Check if the socket is closed or invalid
            sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            return True
        except (socket.error, OSError):
            return False

    def _get_socket(self, scheme, host, port):
        key = scheme + "://" + host
        if self.host not in WEB_URL.sockets or not self._is_socket_valid(
            WEB_URL.sockets[key]
        ):
            WEB_URL.sockets[key] = self._create_socket(
                self.scheme, self.host, self.port
            )
        return WEB_URL.sockets[key]

    def _create_socket(self, scheme, host, port):
        s = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        )
        if scheme == "https":
            cts = ssl.create_default_context()
            s = cts.wrap_socket(s, server_hostname=host)
        s.connect((host, port))
        return s

    def _get_path(self):
        return self.path

    def _get_host(self):
        return self.host

    def _get_scheme(self):
        return self.scheme
