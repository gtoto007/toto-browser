import hashlib
import os
from CacheBrowser import CacheBrowser


def test_cache_asset():
    # Arrange
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, "asset.gif"), "rb") as f:
        asset = f.read()

    ##Act
    cache_browser = CacheBrowser()
    cache_browser.save_to_cache(
        "http://www.example.com/asset.jpg", asset, {"cache-control": "max-age=200"}
    )

    # Assert
    assert cache_browser.has_valid_cache("http://www.example.com/asset.jpg") == True

    retrieved_asset, headers = cache_browser.get_cached_file(
        "http://www.example.com/asset.jpg"
    )

    assert hashlib.md5(asset).hexdigest() == hashlib.md5(retrieved_asset).hexdigest()
    assert headers['cache-control'] == "max-age=200"