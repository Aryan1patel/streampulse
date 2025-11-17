# services/api_gateway/models.py

from sqlalchemy import Column, String, DateTime
from .db import Base
from datetime import datetime

class TrendingNews(Base):
    __tablename__ = "trending_news"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    link = Column(String, nullable=False)
    source = Column(String, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)