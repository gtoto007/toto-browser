import os
import hashlib
import json

from datetime import datetime, timedelta
import re
import time


_cache_dir = "cache"

_caches = {}


class CacheBrowser:
    def __init__(self):
        if not os.path.exists(_cache_dir):
            os.makedirs(_cache_dir)

        if os.path.exists("cache/cache.json"):
            with open("cache/cache.json", "r") as f:
                _caches = json.load(f)
        else:
            _caches = {}
            with open("cache/cache.json", "w") as f:
                json.dump(_caches, f)

    def save_to_cache(self, url, asset, headers):
        if "max-age" not in headers.get("cache-control", ""):
            raise ValueError("No max-age in headers")

        # max-age=1860, s-maxage=1860
        match = re.search(r"max-age=(\d+)", headers.get("cache-control"))
        max_age = int(match.group(1)) if match else ValueError("No max-age in headers")

        file_path = self._generate_file_path(url)
        self._save_to_disk(file_path, asset)
        _caches[file_path] = {
            "expired": datetime.now() + timedelta(seconds=max_age),
            "headers": headers,
        }
        with open("cache/cache.json", "w") as f:
            json.dump(_caches, f, indent=4, default=str)
        return file_path

    def reset(self):
        # remove folder  cache
        if os.path.exists(_cache_dir):
            os.system("rm -rf cache")
        _caches = {}

    def has_valid_cache(self, url):
        file_path = self._generate_file_path(url)
        return (
            os.path.exists(file_path)
            and _caches.get(file_path)["expired"] > datetime.now()
        )

    def _generate_file_path(self, url):
        return os.path.join(_cache_dir, self._md5(url))

    def _md5(self, content):
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def _save_to_disk(self, file_path, asset):

        with open(file_path, "wb") as f:
            if isinstance(asset, str):
                f.write(asset.encode("utf-8"))
            else:
                f.write(asset)

    def get_cached_file(self, url):
        file_path = self._generate_file_path(url)
        print(_caches)
        with open(file_path, "rb") as f:
            return f.read(), _caches[file_path]["headers"]
