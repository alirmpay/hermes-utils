# FastCRW — Hermes Agent Setup Guide

## Directory layout

```
.
├── README.md
└── docker-compose.override.yml
```

---

## 1. First-time setup

```bash
git clone https://github.com/us/crw.git
wget -O docker-compose.override.yml "https://raw.githubusercontent.com/alirmpay/hermes-utils/refs/heads/main/crawler/docker-compose.override.yml"
```

---

## 2. Start

```bash
docker compose up -d
docker compose logs -f crw    # watch for startup errors
```

Smoke test with:

```bash
curl -X POST http://localhost:3000/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 3}'
```
