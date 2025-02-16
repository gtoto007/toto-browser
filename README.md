# Toto Web Browser

A basic web browser that can load web pages and display their content for educational purposes.

It supports rendering web pages from http, https, and data URLs, as well as displaying the source code of web pages.

## Features

- Supports HTTP, HTTPS, and data URLs
- View page source with `view-source:` prefix
- Basic HTML rendering

## Usage

```python
# Load a webpage
render("https://example.com")

# View page source
render("view-source:https://example.com")

# Load HTML directly
render("data:text/html,<h1>Hello world!</h1>")
```

## Requirements

- Python 3.x
