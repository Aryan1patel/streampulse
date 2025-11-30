from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db import Base, engine, SessionLocal
from services.api_gateway.crud import get_latest_trending
from .crud import get_latest_trending

Base.metadata.create_all(bind=engine)

app = FastAPI(title="StreamPulse API Gateway")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/trending")
def trending(limit: int = 50, db: Session = Depends(get_db)):
    rows = get_latest_trending(db, limit)
    return [
        {
            "id": r.id,
            "title": r.title,
            "link": r.link,
            "source": r.source,
            "fetched_at": r.fetched_at
        }
        for r in rows
    ]

@app.get("/trending/latest")
def latest_trending(db: Session = Depends(get_db)):
    rows = get_latest_trending(db, 1)  # limit = 1
    if not rows:
        return {"message": "No trending news yet."}

    r = rows[0]
    return {
        "id": r.id,
        "title": r.title,
        "link": r.link,
        "source": r.source,
        "fetched_at": r.fetched_at
    }