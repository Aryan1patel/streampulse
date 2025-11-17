from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import TrendingNews

def get_latest_trending(db, limit=50):
    stmt = (
        select(TrendingNews)
        .order_by(TrendingNews.fetched_at.desc())
        .limit(limit)
    )
    
    result = db.execute(stmt).scalars().all()
    return result