from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String)
    provider = Column(String)

    resume_skills = Column(Text)
    job_skills = Column(Text)
    matched_skills = Column(Text)
    missing_skills = Column(Text)
    matched_categories = Column(Text)

    match_percent = Column(Integer)
    category_score = Column(Integer)
    final_score = Column(Integer)
    ai_score = Column(Integer)

    summary = Column(Text)
    suggestions = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)