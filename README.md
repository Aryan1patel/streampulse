# StreamPulse

StreamPulse is a real-time news trend analysis and visualization platform. It ingests news data, processes it to identify trends, and visualizes them in a modern web interface.

## 🚀 Getting Started

### Prerequisites

- **Docker** and **Docker Compose** installed on your machine.
- **Node.js** (v20+) and **npm** (for local frontend development).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd streampulse
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory (or use the one provided) and add your API keys:
    ```bash
    GNEWS_API_KEY=your_api_key_here
    ```

3.  **Start the Services:**
    Run the entire stack using Docker Compose:
    ```bash
    docker-compose up --build -d
    ```

4.  **Access the Application:**
    - **Frontend:** [http://localhost:3000](http://localhost:3000)
    - **API Gateway:** [http://localhost:8000/docs](http://localhost:8000/docs)
    - **Redpanda Console:** [http://localhost:8080](http://localhost:8080) (if enabled)

## 🏗 Architecture

StreamPulse follows a microservices architecture:

### Services

-   **`trending_ingestor`**: Fetches raw news data from external APIs (e.g., GNews) and publishes to Redpanda.
-   **`normalizer`**: Cleans and standardizes raw data.
-   **`trending_store`**: Consumes cleaned data and stores it in Postgres.
-   **`keyword_extractor`**: Extracts keywords from news articles.
-   **`related_fetcher`**: Fetches related content based on keywords.
-   **`api_gateway`**: FastAPI-based gateway that exposes data to the frontend.

### Infrastructure

-   **Redpanda**: High-performance streaming data platform (Kafka-compatible).
-   **PostgreSQL**: Relational database for metadata and structured data.
-   **Redis**: Caching layer for high-speed access.
-   **Qdrant**: Vector database for similarity search.

### Frontend

Built with **Next.js 16**, **React 19**, and **Tailwind CSS 4**.

## 🛠 Development

To run the frontend locally:

```bash
cd frontend
npm install
npm run dev
```
