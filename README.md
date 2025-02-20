# Toto Web Browser

A basic web browser that can load web pages and display their content for educational purposes.

It supports rendering web pages from http, https, and data URLs, as well as displaying the source code of web pages.

## Features

- Supports HTTP, HTTPS, and data URLs
- View page source with `view-source:` prefix
- Basic HTML rendering
- Persistent connection for requests with the same host

## Usage

```python
# Load a webpage
python3 browser.py https://example.com

# View page source
python3 browser.py view-source:https://example.com

# Loads multiple webpages
python3 browser.py https://example.com https://www.freesoft.org/CIE/Topics/88.htm

# Load HTML directly
python3 browser.py 'data:text/html,<h1>Hello world!</h1>'
```

## Requirements

- Python 3.x
