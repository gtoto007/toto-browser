class DATA_URL:
    def __init__(self, url):
        assert url.startswith("data:")  # e.g. "data:text/html,Hello world!"
        self.view_source = False
        self.type = url.split(":", 1)[1]
        self.type, self.body = self.type.split(",", 1)

    def request(self):
        return [], self.body
