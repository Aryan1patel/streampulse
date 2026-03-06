# ⚡ StreamPulse

**Real-time news trend analysis & market impact visualization**

[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Redpanda](https://img.shields.io/badge/Redpanda-Streaming-E7274C?style=flat-square&logo=apachekafka)](https://redpanda.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

StreamPulse is a **production-style streaming data platform** that ingests trending business news in real time, enriches each article with NLP-powered keyword extraction, sentiment analysis, and event classification — then runs an ML ensemble to estimate **short-term market impact** for detected companies.

</div>

---

## 📸 Preview

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/190da523-19fc-44db-887a-16801a4529ee" width="100%"/></td>
    <td><img width="1709" height="984" alt="Screenshot 2026-03-06 at 11 03 20 PM" src="https://github.com/user-attachments/assets/da26a62e-6a80-458f-a8eb-58c38392355a" />
      </td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/e2e2068b-f1a9-460e-b8ff-edfc78c2a23f" width="100%"/></td>
    <td><img width="1710" height="984" alt="image" src="https://github.com/user-attachments/assets/eb3bc62d-7ce0-4c77-b990-136b3a347b59" />
</td>
  </tr>
</table>

<!-- Uncomment and update the path when you have a screenshot:
![StreamPulse Dashboard](./docs/screenshot.png)
-->

---

## ✨ What It Does

| Stage | What happens |
|---|---|
| 📡 **Ingest** | Polls GNews (+ optional sources) and streams raw articles into Redpanda |
| 🧹 **Normalize** | Cleans, deduplicates, and standardises fields, then republishes |
| 💾 **Store** | Persists cleaned articles into PostgreSQL via a dedicated consumer |
| 🧠 **Understand** | Extracts keywords, detects companies, classifies event type, scores sentiment & severity |
| 🔍 **Contextualise** | Fans out to related articles and quick market snapshots in parallel |
| 📊 **Predict** | Engineers features, runs similarity search against historical events (Qdrant), returns a market-impact estimate with confidence + explainers |
| 🖥️ **Visualise** | Serves everything through a snappy Next.js dashboard with charting and a deep-dive view |

---

## 🏗️ Architecture

StreamPulse is built as a **microservices pipeline** — each stage is an independent, replaceably-restartable service communicating through Redpanda (Kafka-compatible streaming).

```
┌──────────────────────────────────────────────────────────────────────┐
│                          STREAMING PIPELINE                          │
│                                                                      │
│  GNews API ──► trending_ingestor ──► [trending_raw] ──► normalizer   │
│                                                              │        │
│                                              [trending_clean]│        │
│                                                              ▼        │
│                                                    trending_store     │
│                                                          │            │
│                                                      PostgreSQL       │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                   ON-DEMAND ANALYSIS (per headline)                  │
│                                                                      │
│  Frontend ──► api_gateway ──► keyword_extractor                      │
│                          └──► related_fetcher                        │
│                          └──► deep_dive_worker ──► Qdrant (similarity)│
│                                     │                                │
│                                PostgreSQL (prediction history)       │
└──────────────────────────────────────────────────────────────────────┘
```

### Services & Ports

| Service | Container | Host Port | Description |
|---|---|:---:|---|
| **API Gateway** | `streampulse-api` | `8000` | Main REST API + OpenAPI docs |
| **Related Fetcher** | `streampulse-related-fetcher` | `7001` | Parallel related-article fan-out |
| **Keyword Extractor** | `streampulse-keyword-extractor` | `7002` | NLP: keywords, sentiment, event type |
| **Market Data** | `streampulse-market-data` | `7003` | Stock price / market snapshots |
| **Deep Dive Worker** | `streampulse-deep-dive` | `7004` | ML ensemble market-impact prediction |
| **Redpanda** | `streampulse-redpanda` | `9093` | Kafka-compatible message broker |
| **PostgreSQL** | `streampulse-postgres` | `5433` | Relational store (articles + predictions) |
| **Redis** | `streampulse-redis` | `6379` | Response cache layer |
| **Qdrant** | `streampulse-qdrant` | `6333` | Vector DB for similarity search |

### Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16, React 19, Tailwind CSS 4, Recharts, TypeScript |
| **Backend** | Python, FastAPI, yfinance, pandas, numpy, scikit-learn |
| **Streaming** | Redpanda (Kafka-compatible) |
| **Databases** | PostgreSQL · Redis · Qdrant |
| **Infrastructure** | Docker, Docker Compose |

---

## 🚀 Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (includes Docker Compose)
- Node.js v20+ *(only needed for local frontend dev)*

### 1 — Clone & configure

```bash
git clone https://github.com/your-username/streampulse.git
cd streampulse
```

Create a `.env` file in the root:

```env
GNEWS_API_KEY=your_gnews_api_key_here
```

> Get a free GNews key at [gnews.io](https://gnews.io). Some related-news fetchers accept additional keys — if absent, they fail gracefully and return partial results.

### 2 — Start the full stack

```bash
docker-compose up -d --build
```

All services will spin up. The first build may take a few minutes.

### 3 — Verify everything is up

| Endpoint | What it checks |
|---|---|
| `http://localhost:8000/docs` | Interactive API docs (Swagger UI) |
| `http://localhost:8000/trending?limit=5` | Latest trending articles |
| `http://localhost:7002/keywords?headline=Apple+earnings` | Keyword extractor smoke-test |
| `http://localhost:7004/health` | Deep-dive worker health |

### 4 — Run the end-to-end test

```bash
python3 test_end_to_end.py
```

This exercises the full pipeline: trending feed → keyword extraction → related context → market-impact prediction.

---

## 🖥️ Frontend (Local Dev)

The Next.js UI lives in `frontend/`. API routes under `frontend/app/api/*` proxy to backend services so the browser never needs to know internal URLs.

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

**Environment overrides** (create `frontend/.env.local`):

```env
API_GATEWAY_URL=http://localhost:8000
KEYWORD_EXTRACTOR_URL=http://localhost:7002
RELATED_FETCHER_URL=http://localhost:7001
```

### Pages

| Route | Description |
|---|---|
| `/` | Home — trending news feed |
| `/news/[id]` | Full article view |
| `/deep-dive/[symbol]` | ML market-impact analysis for a stock |

---

## 📂 Project Structure

```
streampulse/
├── services/
│   ├── api_gateway/          # Main REST API (FastAPI)
│   ├── ingestors/            # trending_ingestor — polls GNews
│   ├── normalizer/           # Cleans raw articles
│   ├── trending_store/       # Consumes cleaned data → Postgres
│   ├── keyword_extractor/    # NLP enrichment service
│   ├── related_fetcher/      # Fan-out to related articles
│   ├── market_data/          # Stock price lookups
│   └── deep_dive_worker/     # ML ensemble + Qdrant similarity
├── frontend/                 # Next.js 16 app
│   ├── app/                  # App Router pages + API routes
│   ├── components/           # Shared React components
│   └── lib/                  # Utilities, types, helpers
├── libs/                     # Shared Python utilities
├── infra/                    # Infrastructure configs (Redpanda, etc.)
├── data/                     # Static reference data (companies.csv)
├── docker-compose.yml
└── test_end_to_end.py
```

---

## 🔑 Code Entry Points

If you want to understand the project quickly, start here:

1. **Streaming pipeline** — `services/ingestors/trending_ingestor/` → `services/normalizer/` → `services/trending_store/`
2. **API Gateway** — `services/api_gateway/main.py` (source of truth for `/trending`)
3. **Deep Dive ML** — `services/deep_dive_worker/feature_engineering.py` + `ml_model.py` + `seed_qdrant.py`
4. **Frontend pages** — `frontend/app/` (especially `deep-dive/[symbol]/page.tsx`)
5. **E2E test** — `test_end_to_end.py` shows all HTTP calls and expected response shapes

---

## 🛠️ Troubleshooting

<details>
<summary><strong>Port 5433 already in use (Postgres)</strong></summary>

Another Postgres instance is already bound to port 5433. Stop it first:

```bash
# Find what's using the port
lsof -i :5433
# Then kill that process, or change the host port in docker-compose.yml
```
</details>

<details>
<summary><strong>Container name conflicts</strong></summary>

```bash
docker-compose down
docker rm -f $(docker ps -a -q --filter "name=streampulse")
docker-compose up -d --build
```
</details>

<details>
<summary><strong>Existing Docker network warning</strong></summary>

```
a network with name streampulse-network exists but was not created for project ...
```

This is harmless — Docker is reusing an existing network. The stack will still start correctly.
</details>

<details>
<summary><strong>Connection refused on localhost:8000</strong></summary>

The stack isn't running yet. Start it with:

```bash
docker-compose up -d --build
```

Then wait ~30 seconds for all services to become healthy before hitting endpoints.
</details>

<details>
<summary><strong>Frontend can't reach backend</strong></summary>

Ensure the `frontend/.env.local` URL variables point to the correct host/port. If running the frontend outside Docker, the defaults (`localhost:8000`, etc.) should work as-is.
</details>

---

## 🗺️ Roadmap

- [ ] Redpanda Console UI integration
- [ ] WebSocket-based live feed on the frontend
- [ ] Expanded ML model evaluation & monitoring dashboard
- [ ] Structured logging + distributed tracing (OpenTelemetry)
- [ ] CI pipeline with unit + integration tests

---

## 📄 License

This project is released under the [MIT License](LICENSE).

> StreamPulse is prototype/educational-grade. Before production use, add proper secrets management, rate limiting, structured logging, robust scraping fallbacks, and model monitoring.
