# LinkPulse

A small URL shortener with a live link list and click counts. Built with Python's standard library, SQLite, and vanilla JavaScript.

## Run locally

Requires Python 3.9 or newer. No package installation is needed.

```bash
cd linkpulse
python3 server.py
```

Open <http://localhost:8000>. Links and click counts are stored in `linkpulse.db` in this folder.

## What it demonstrates

- A JSON API for creating and listing links
- URL validation and parameterized SQLite queries
- Short-code generation and HTTP redirects
- Persistent click tracking
- A responsive dashboard that talks to the API

## API

- `GET /api/links` — list links and click counts
- `POST /api/links` — create a link with JSON body `{"url":"https://example.com"}`
- `GET /{code}` — redirect to the destination and increment its click count

## Current scope

This is a learning project and local demo. It does not yet include user accounts, rate limiting, expiry dates, or production deployment. Click counts update when the dashboard is refreshed.
