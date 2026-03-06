\# StreamPulse

StreamPulse is a real-time news-to-signal pipeline: it ingests trending news, cleans it, stores it, extracts “what this is about” (keywords + sentiment + event type), finds related context, and optionally runs an ML “deep dive” to estimate short-term market impact for a detected company.

If you just ran the end-to-end test, you’ve exercised the core workflow:

1) **Trending feed** → `GET http://localhost:8000/trending?limit=5`
2) **Keyword + sentiment** → `GET http://localhost:7002/keywords?...`
3) **Related context** → `GET http://localhost:7001/fetch_related?...`
4) **Deep dive prediction** → `GET http://localhost:7004/deep-dive?...`

---

## What this project does (in plain English)

- **Continuously collect** trending business news.
- **Normalize + store** it so the UI and APIs are fast and consistent.
- **Understand each headline** (keywords, companies, event type, sentiment, severity).
- **Fetch context** (related stories + quick market data).
- **Generate an impact view** (direction + expected move + confidence + explainers).

---

## Why these technologies

StreamPulse is designed like a production data product: ingestion is streaming, storage is durable, query paths are fast, and analysis is modular.

- **FastAPI (Python)**: fast iteration, great for microservices, automatic docs (`/docs`). Most services are small HTTP APIs.
- **Redpanda (Kafka-compatible streaming)**: decouples ingestion from processing. Services can be restarted/replaced without losing the pipeline. Redpanda is lightweight and works well on ARM/macOS.
- **PostgreSQL**: system-of-record for normalized trending articles and prediction history.
- **Redis**: intended as a fast cache layer (useful for hot endpoints like trending feeds).
- **Qdrant (vector DB)**: similarity search for “find similar past events” used by deep-dive pattern features.
- **Next.js (React)**: fast UI development with server routes (`frontend/app/api/*`) that proxy to backend services.
- **yfinance/pandas/numpy**: quick market data + feature computation.

---

## Architecture (how data moves)

### A) Streaming ingestion pipeline (always-on)

1. **`trending_ingestor`** polls external sources and publishes raw articles to Kafka/Redpanda topic `trending_raw`.
2. **`normalizer`** consumes `trending_raw`, cleans/standardizes fields, and publishes to `trending_clean`.
3. **`trending_store`** consumes `trending_clean` and upserts into Postgres.
4. **`api_gateway`** serves the stored articles to the frontend (`/trending`).

This design lets you add more processors later (dedupe, enrichment, embeddings, etc.) without changing the ingestor.

### B) On-demand analysis pipeline (per headline)

When a user (or test) selects a headline:

1. **`keyword_extractor`** scrapes the article (when URL is available) and returns:
   - event type (e.g., earnings)
   - sentiment label + score
   - severity
   - detected companies + keywords
2. **`related_fetcher`** fans out to multiple sources in parallel and returns related articles + (optional) quick market lookup.
3. **`deep_dive_worker`** pulls market data + related sentiment, engineers features, runs an ensemble prediction, and logs results to Postgres.

---

## Services and ports

From `docker-compose.yml`:

| Component | Container | Host Port | Notes |
|---|---:|---:|---|
| API Gateway | `streampulse-api` | `8000` | Trending endpoints + OpenAPI docs |
| Related Fetcher | `streampulse-related-fetcher` | `7001` | Exposes `/fetch_related` (container listens on `7000`) |
| Keyword Extractor | `streampulse-keyword-extractor` | `7002` | Exposes `/keywords` |
| Market Data | `streampulse-market-data` | `7003` | Exposes `/stock/{symbol}` etc. |
| Deep Dive | `streampulse-deep-dive` | `7004` | Exposes `/deep-dive` |
| Redpanda (Kafka) | `streampulse-redpanda` | `9093` | Kafka exposed as `localhost:9093` (container listens `9092`) |
| Postgres | `streampulse-postgres` | `5433` | DB exposed as `localhost:5433` |
| Redis | `streampulse-redis` | `6379` | Cache |
| Qdrant | `streampulse-qdrant` | `6333` | Vector DB |

---

## Quick start (Docker)

### Prereqs

- Docker + Docker Compose
- (Optional) Node.js 20+ for local frontend development

### 1) Configure environment

Create a `.env` file in the repo root:

```bash
GNEWS_API_KEY=your_key_here
```

Note: some related-news fetchers may require extra API keys (depending on which fetchers you enable/configure). If a fetcher lacks a key, it should fail gracefully and the service still returns partial results.

### 2) Start everything

```bash
docker-compose up -d --build
```

### 3) Verify

- API docs: `http://localhost:8000/docs`
- Trending: `http://localhost:8000/trending?limit=5`
- Keyword extractor: `http://localhost:7002/keywords?headline=Test`
- Deep dive health: `http://localhost:7004/health`

---

## Frontend

The UI lives in `frontend/` (Next.js App Router). It includes API routes under `frontend/app/api/*` that proxy to the backend services so the browser doesn’t need to know internal service URLs.

Run locally:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

You can override backend URLs (useful if the frontend runs outside Docker) via:

- `API_GATEWAY_URL` (default `http://localhost:8000`)
- `KEYWORD_EXTRACTOR_URL` (default `http://localhost:7002`)
- `RELATED_FETCHER_URL` (default `http://localhost:7001`)

---

## Running the end-to-end test

This is the same flow you posted:

```bash
python3 test_end_to_end.py
```

If you see `Connection refused` on `localhost:8000`, the stack is not running. Start it with `docker-compose up -d --build`.

---

## What to explore next (recommended)

If you want to really understand the project quickly, these are the best entry points:

1. **End-to-end client**: `test_end_to_end.py` shows the exact HTTP calls and the expected response shapes.
2. **API Gateway**: `services/api_gateway/main.py` is the “source of truth” for `/trending`.
3. **Streaming pipeline**:
   - `services/ingestors/trending_ingestor/` (producer)
   - `services/normalizer/` (cleaning)
   - `services/trending_store/main.py` (consumer → Postgres)
4. **Deep dive internals**:
   - `services/deep_dive_worker/feature_engineering.py`
   - `services/deep_dive_worker/ml_model.py` (ensemble)
   - `services/deep_dive_worker/seed_qdrant.py` (similarity base)
5. **Frontend pages**: `frontend/app/` (especially the deep-dive route).

---

## Troubleshooting

### Container name conflicts

If you see an error like:
`Conflict. The container name "/streampulse-…" is already in use`

Clean old containers and restart:

```bash
docker-compose down
docker rm -f $(docker ps -a -q --filter "name=streampulse")
docker-compose up -d --build
```

### Existing Docker network warning

You may see:
`a network with name streampulse-network exists but was not created for project ...`

This is usually harmless. It means an existing network is reused.

---

## License / Notes

This repo is intended as an educational + prototype-grade system demonstrating streaming ingestion + enrichment + ML analysis. Before production use, you’d typically add:

- proper secrets management
- structured logging + tracing
- rate limiting + retries
- robust scraping fallbacks
- model evaluation + monitoring
- CI for unit/integration tests
