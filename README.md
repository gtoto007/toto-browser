# Toto Web Browser

A basic web browser that can load web pages and display their content for educational purposes.

It supports rendering web pages from http, https, and data URLs, as well as displaying the source code of web pages.

## Features

- Supports HTTP, HTTPS, and data URLs
- View page source with `view-source:` prefix
- Basic HTML rendering
- Persistent connection for requests with the same host
- Supported Response Headers
    - `cache-control`: Supports `max-age` directive (specifies the maximum amount of time a resource is considered fresh)
    - `content-encoding`: Supports `gzip` compression (allows response to be compressed )
    - `transfer-encoding`: Supports `chunked` directive (allows response to be received in a series of chunks)


## Usage

```python
# Load a webpage
python3 main.py https://example.com

# View page source
python3 main.py view-source:https://example.com

# Loads multiple webpages
python3 main.py https://example.com https://www.freesoft.org/CIE/Topics/88.htm

# Load HTML directly
python3 main.py 'data:text/html,<h1>Hello world!</h1>'
```

## Requirements

- Python 3.x
