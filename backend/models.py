from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    drug_name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="active")  # active, paused, completed
    frequency = Column(String(20), default="daily")  # realtime, daily, weekly
    platforms = Column(JSON, default=["reddit", "twitter"])
    keywords = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_posts = Column(Integer, default=0)
    total_signals = Column(Integer, default=0)

    posts = relationship("Post", back_populates="project")
    signals = relationship("Signal", back_populates="project")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    source = Column(String(50))  # reddit, twitter, forum
    source_post_id = Column(String(200))
    raw_content = Column(Text)
    anonymized_content = Column(Text)
    author_hash = Column(String(64))
    url = Column(String(500))
    posted_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    extracted_adrs = Column(JSON, default=[])
    confidence_score = Column(Float, default=0.0)
    is_first_person = Column(Boolean, default=False)
    location = Column(String(100))
    pii_detected = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    subreddit = Column(String(100))

    project = relationship("Project", back_populates="posts")


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    drug_name = Column(String(100), nullable=False)
    adr_term = Column(String(200), nullable=False)
    adr_category = Column(String(100))
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    report_count = Column(Integer, default=1)
    unique_sources = Column(Integer, default=1)
    prr_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    is_on_label = Column(Boolean, default=True)
    priority = Column(String(20), default="LOW")  # HIGH, MEDIUM, LOW
    status = Column(String(20), default="active")  # active, resolved, false_positive
    growth_rate = Column(Float, default=0.0)  # percentage growth per week
    source_posts = Column(JSON, default=[])
    timeline = Column(JSON, default=[])
    locations = Column(JSON, default=[])

    project = relationship("Project", back_populates="signals")
    reports = relationship("Report", back_populates="signal")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    signal_id = Column(Integer, ForeignKey("signals.id"))
    generated_at = Column(DateTime, default=datetime.utcnow)
    report_format = Column(String(20), default="json")  # json, pdf
    title = Column(String(300))
    content = Column(JSON)
    status = Column(String(20), default="draft")  # draft, reviewed, submitted
    reviewer_notes = Column(Text)

    signal = relationship("Signal", back_populates="reports")
