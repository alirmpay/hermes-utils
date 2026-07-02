# Text Embedding — Hermes Agent Setup Guide

## Directory layout

```
.
├── docker-compose.yml
├── Dockerfile
├── server.py
└── README.md
```

---

## 1. First-time setup

```bash
docker compose up -d
```

Note: In case you don't want to rebuild the image, uncomment image in `docker-compose.yml` file and
comment build out.

---

## 2. Test

```bash

curl http://localhost:8989/embed -X POST -H 'Content-Type: application/json' \
  -d '{"inputs":"What is Deep Learning?"}'
```
