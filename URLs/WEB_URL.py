import socket
import ssl
from Cache import Cache


class WEB_URL:
    # define a static dictionary to store the sockets for each single url
    sockets = {}
    redirect_count = 0
    MAX_REDIRECTS = 5

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
        """
        Performs an HTTP/HTTPS request or file read based on the URL scheme.

        Returns:
            tuple: A tuple containing three elements:
                - headers (dict): Response headers for web requests, empty list for file requests
                - status (int): HTTP status code (200 for successful file requests)
                - content (str/bytes): The response body or file contents

        Note:
            For web requests, it first checks the cache before making a new request.
            For file requests, it reads directly from the local filesystem.
        """
        if self.scheme == "file":
            return self._file_request()
        else:
            return self._web_request()

    def _file_request(self):
        with open(self.path, "r") as f:
            return {}, 200, f.read()

    def _web_request(self):
        cache = Cache()
        if cache.has_valid_cache(self.host):
            headers, content = cache.get_cached_file(self.host)
            return headers, 200, content

        request = f"GET {self.path} HTTP/1.1\r\n"

        headers = []
        headers.append(f"Host: {self.host}")
        headers.append("Connection: keep-alive")
        headers.append("User-Agent: TotoBrowser")
        headers.append("Accept-Encoding: gzip")

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

        if (
            status is not None
            and status >= 300
            and status < 400
            and "location" in response_headers
        ):
            return self.redirect(response_headers["location"])

        WEB_URL.redirect_count = 0

        if "chunked" in response_headers.get("transfer-encoding", ""):
            content = b""
            while True:
                line = response.readline()
                if line == b"\r\n":
                    continue
                chunk_size = int(line, 16)
                if chunk_size == 0:
                    response.readline()
                    break
                content += response.read(chunk_size)
        else:
            content = response.read(int(response_headers.get("content-length", 0)))

        if response_headers.get("content-encoding") == "gzip":
            import gzip

            content = gzip.decompress(content)

        if "max-age" in response_headers.get("cache-control", ""):
            cache.save_to_cache(self.original_url, content, response_headers)

        try:
            content = content.decode("utf-8")
        except UnicodeDecodeError:
            pass

        return response_headers, status, content

    def redirect(self, url):
        if WEB_URL.redirect_count >= WEB_URL.MAX_REDIRECTS:
            WEB_URL.redirect_count = 0
            raise "Too many redirects"

        WEB_URL.redirect_count += 1
        browser = WEB_URL(url)
        return browser.request()

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
