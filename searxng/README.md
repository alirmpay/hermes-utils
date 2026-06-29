# SearXNG — Hermes Agent Setup Guide

## Directory layout

```
.
├── docker-compose.yml
└── core-config/
    └── settings.yml          # ← your curated config
```

---

## 1. First-time setup

```bash
# Create the config directory SearXNG mounts
mkdir -p core-config

# Copy settings.yml into place
cp settings.yml core-config/settings.yml

# Generate a strong secret key and paste it into settings.yml
python3 -c "import secrets; print(secrets.token_hex(32))"
# → Edit searxng/settings.yml: replace REPLACE_WITH_STRONG_RANDOM_SECRET
```

---

## 2. File permissions

SearXNG inside the container runs as UID/GID 977 (varies by image).
The mounted directory needs to be writable so the container can write
`uwsgi.ini` and other runtime files.

```bash
chmod 775 core-config/
chmod 664 core-config/settings.yml
```

If you hit permission errors, try:

```bash
sudo chown -R 977:977 core-config/
```

---

## 3. Start

```bash
docker compose up -d
docker compose logs -f searxng    # watch for startup errors
```

Test JSON output (what Hermes / Firecrawl will call):

```bash
curl -s "http://127.0.0.1:8080/search?q=arxiv+transformers&format=json" | jq '.results[0]'
```

---

## 4. How Hermes should call SearXNG

### Endpoint

```
POST http://127.0.0.1:8080/search
Content-Type: application/x-www-form-urlencoded
```

### Parameters

| Parameter  | Values / notes |
|------------|----------------|
| `q`        | search query |
| `format`   | `json` (required for machine use) |
| `categories` | `general`, `science`, `it`, `images`, `news`, `social media`, `shopping` |
| `language` | `en` (or `en-US`) |
| `safesearch` | `1` (moderate; matches config default) |
| `pageno`   | `1`, `2`, … |

### Example

```bash
# Academic search
curl -s -X POST http://127.0.0.1:8080/search \
  -d "q=attention+is+all+you+need&categories=science&format=json&language=en" \
  | jq '.results[] | {title, url, content}'

# Code search
curl -s -X POST http://127.0.0.1:8080/search \
  -d "q=pytorch+dataloader+multiprocessing&categories=it&format=json" \
  | jq '.results[] | {title, url}'

# Image search
curl -s -X POST http://127.0.0.1:8080/search \
  -d "q=transformer+architecture+diagram&categories=images&format=json" \
  | jq '.results[] | {title, url, img_src}'
```

### JSON response shape

```json
{
  "query": "...",
  "number_of_results": 42,
  "results": [
    {
      "url": "https://...",
      "title": "...",
      "content": "...",
      "engine": "arxiv",
      "score": 1.0,
      "category": "science",
      "publishedDate": "2024-01-15T00:00:00"
    }
  ],
  "answers": [],
  "corrections": [],
  "infoboxes": [],
  "suggestions": [],
  "unresponsive_engines": []
}
```

---

## 5. Engine selection rationale

| Engine | Category | Why included |
|--------|----------|--------------|
| Qwant | general, images, news | API-friendly, EU-based, low CAPTCHA rate |
| Brave | general, images, news, shopping | Own index, API access, reliable |
| DuckDuckGo | general, images | Reliable fallback, no account needed |
| Mwmbl | general | Open-source crawler, zero friction |
| Google | general | High-quality fallback; CAPTCHA-prone, lower weight |
| Bing | general | Fallback only |
| arXiv | science | Official API, no rate-limit issues |
| PubMed | science | Official NCBI API |
| Semantic Scholar | science | Free API, excellent AI/ML coverage |
| Crossref | science | DOI metadata, free API |
| OpenAlex | science | Open access papers, free API |
| GitHub | it | Repos, issues, READMEs |
| GitHub Code | it | Code-level search |
| Stack Overflow | it | Q&A, highly relevant for Hermes |
| MDN | it | Web standards reference |
| Hugging Face | it, science | Models, datasets, papers |
| Reddit | social media | Community knowledge, occasionally noisy |
| Brave News | news | Clean news API |
| Qwant News | news | EU alternative news index |
| Brave Shopping | shopping | Low-friction product results |

---

## 6. Upgrading SearXNG

1. Check the [SearXNG changelog](https://github.com/searxng/searxng/releases).
2. Update the image tag in `docker-compose.yml`.
3. Run `docker compose pull && docker compose up -d`.
4. Check `unresponsive_engines` in a test query to detect newly broken engines.
5. Remove broken engines from `keep_only` in `settings.yml`.

Because `use_default_settings: true` with `keep_only` is used, new engines
added upstream will **not** appear automatically — you opt in explicitly.
This is intentional for a curated production config.

---

## 7. CAPTCHA mitigation tips

- Valkey caches engine tokens (DuckDuckGo vqd, Startpage code, etc.) — keep
  Valkey running continuously to avoid cold-start CAPTCHA triggers.
- If an engine hits `SearxEngineAccessDenied`, it is banned for 24 h
  automatically (`suspended_times` in settings.yml).
- Google is the most CAPTCHA-prone; it has `weight: 1` and is a fallback only.
- Consider adding a SearXNG [limiter](https://docs.searxng.org/admin/searx.limiter.html)
  if you ever expose this beyond localhost.

---

## 8. Monitoring unresponsive engines

```bash
# Quick health check — shows which engines failed in the last query
curl -s "http://127.0.0.1:8080/search?q=test&format=json" \
  | jq '.unresponsive_engines'
```

Engines that fail repeatedly should be removed from `keep_only` to reduce
latency (SearXNG still waits up to `request_timeout` for them).
