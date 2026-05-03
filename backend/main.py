from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from pydantic import BaseModel
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from database import engine, get_db, SessionLocal
from models import Base, Project, Post, Signal, Report
from nlp.adr_extractor import process_post
from signals.label_comparator import compare_signal_to_label, get_drug_label
from signals.prr_calculator import calculate_prr, calculate_growth_rate
from reports.generator import generate_pv_report
from crawlers.reddit_crawler import search_reddit

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PharmaSentinel API",
    description="Real-Time Drug Safety Signal Detection",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Pydantic Schemas ─────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    drug_name: str
    description: Optional[str] = ""
    frequency: Optional[str] = "daily"
    platforms: Optional[List[str]] = ["reddit", "twitter"]
    keywords: Optional[List[str]] = []


class ProjectResponse(BaseModel):
    id: int
    name: str
    drug_name: str
    description: Optional[str]
    status: str
    frequency: str
    platforms: List[str]
    total_posts: int
    total_signals: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Startup: Seed demo data ──────────────────────────────────────────────────

@app.on_event("startup")
async def seed_demo_data():
    db = SessionLocal()
    try:
        if db.query(Project).count() > 0:
            return
        _seed_database(db)
    finally:
        db.close()


def _seed_database(db: Session):
    from crawlers.mock_generator import MOCK_REDDIT_POSTS
    from nlp.adr_extractor import process_post
    from signals.label_comparator import compare_signal_to_label
    from signals.prr_calculator import calculate_prr

    demo_drugs = [
        {
            "name": "Azithromycin Safety Watch",
            "drug_name": "azithromycin",
            "description": "Monitoring social media for unreported side effects of Azithral/Azee",
            "frequency": "realtime",
            "platforms": ["reddit", "twitter"],
        },
        {
            "name": "Paracetamol Long-term Use",
            "drug_name": "paracetamol",
            "description": "Tracking liver and kidney reports for long-term paracetamol users",
            "frequency": "daily",
            "platforms": ["reddit", "twitter"],
        },
        {
            "name": "Ciprofloxacin Monitoring",
            "drug_name": "ciprofloxacin",
            "description": "Monitoring tendon and CNS side effect reports for fluoroquinolones",
            "frequency": "daily",
            "platforms": ["reddit"],
        },
        {
            "name": "Metformin ADR Tracker",
            "drug_name": "metformin",
            "description": "Tracking B12 deficiency and psychological effects in diabetic patients",
            "frequency": "weekly",
            "platforms": ["reddit", "twitter"],
        },
    ]

    for drug_data in demo_drugs:
        project = Project(**drug_data, total_posts=0, total_signals=0)
        db.add(project)
        db.flush()

        mock_posts = MOCK_REDDIT_POSTS.get(drug_data["drug_name"], [])
        post_objs = []
        for raw in mock_posts:
            nlp_result = process_post(raw["content"], raw.get("author", ""))
            posted_at = datetime.fromisoformat(raw["posted_at"]) if raw.get("posted_at") else datetime.utcnow()
            post_obj = Post(
                project_id=project.id,
                source=raw.get("source", "reddit"),
                source_post_id=raw.get("id", ""),
                raw_content=raw["content"],
                anonymized_content=nlp_result["anonymized_content"],
                author_hash=nlp_result["author_hash"],
                url=raw.get("url", ""),
                posted_at=posted_at,
                extracted_adrs=nlp_result["extracted_adrs"],
                confidence_score=nlp_result["confidence_score"],
                is_first_person=nlp_result["is_first_person"],
                pii_detected=nlp_result["pii_detected"],
                location=raw.get("location"),
                subreddit=raw.get("subreddit"),
                is_processed=True,
            )
            db.add(post_obj)
            post_objs.append((post_obj, nlp_result))

        db.flush()
        project.total_posts = len(post_objs)

        # Aggregate signals
        adr_counts: Dict[str, Dict] = {}
        for post_obj, nlp_result in post_objs:
            if not nlp_result["is_first_person"] or nlp_result["confidence_score"] < 0.3:
                continue
            for adr in nlp_result["extracted_adrs"]:
                term = adr["term"]
                if term not in adr_counts:
                    adr_counts[term] = {
                        "count": 0, "category": adr["category"],
                        "posts": [], "locations": set()
                    }
                adr_counts[term]["count"] += 1
                adr_counts[term]["posts"].append(post_obj.id)
                if post_obj.location:
                    adr_counts[term]["locations"].add(post_obj.location)

        total_drug_reports = len(post_objs)

        for adr_term, data in adr_counts.items():
            if data["count"] < 1:
                continue

            label_result = compare_signal_to_label(drug_data["drug_name"], adr_term, data["count"])
            prr_result = calculate_prr(data["count"], max(total_drug_reports, data["count"]), adr_term=adr_term)

            # Build timeline (simulate weekly data)
            timeline = []
            for week in range(4):
                timeline.append({
                    "week": f"Week {week + 1}",
                    "count": max(1, data["count"] - (3 - week))
                })

            signal = Signal(
                project_id=project.id,
                drug_name=drug_data["drug_name"],
                adr_term=adr_term,
                adr_category=data["category"],
                report_count=data["count"],
                unique_sources=len(set(data["posts"])),
                prr_score=prr_result["prr"],
                confidence=sum(
                    p.confidence_score for p, _ in post_objs
                    if p.id in data["posts"]
                ) / max(len(data["posts"]), 1),
                is_on_label=label_result["is_on_label"],
                priority=label_result["priority"],
                source_posts=data["posts"],
                timeline=timeline,
                locations=list(data["locations"]),
                growth_rate=calculate_growth_rate(timeline),
                first_detected=datetime.utcnow() - timedelta(days=14),
                last_updated=datetime.utcnow(),
            )
            db.add(signal)

        db.flush()
        project.total_signals = db.query(Signal).filter_by(project_id=project.id).count()

    db.commit()


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "PharmaSentinel API", "version": "1.0.0", "status": "running"}


@app.get("/api/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_projects = db.query(Project).count()
    total_posts = db.query(Post).count()
    total_signals = db.query(Signal).count()
    high_priority = db.query(Signal).filter_by(priority="HIGH").count()
    unlisted_signals = db.query(Signal).filter_by(is_on_label=False).count()

    return {
        "total_projects": total_projects,
        "total_posts_analyzed": total_posts,
        "total_signals": total_signals,
        "high_priority_signals": high_priority,
        "unlisted_adrs": unlisted_signals,
        "drugs_monitored": total_projects,
    }


@app.get("/api/projects", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@app.get("/api/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    signals = db.query(Signal).filter_by(project_id=project_id).order_by(
        Signal.priority.desc(), Signal.report_count.desc()
    ).all()

    label_info = get_drug_label(project.drug_name)

    return {
        "id": project.id,
        "name": project.name,
        "drug_name": project.drug_name,
        "description": project.description,
        "status": project.status,
        "frequency": project.frequency,
        "platforms": project.platforms,
        "total_posts": project.total_posts,
        "total_signals": project.total_signals,
        "created_at": project.created_at,
        "drug_info": label_info,
        "signals": [_signal_to_dict(s) for s in signals],
    }


@app.post("/api/projects")
def create_project(data: ProjectCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = Project(
        name=data.name,
        drug_name=data.drug_name.lower().strip(),
        description=data.description,
        frequency=data.frequency,
        platforms=data.platforms,
        keywords=data.keywords,
        total_posts=0,
        total_signals=0,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    background_tasks.add_task(run_crawl, project.id)
    return {"id": project.id, "message": "Project created. Crawling started.", "status": "crawling"}


@app.post("/api/projects/{project_id}/crawl")
def trigger_crawl(project_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    background_tasks.add_task(run_crawl, project_id)
    return {"message": "Crawl triggered", "project_id": project_id}


def run_crawl(project_id: int):
    db = SessionLocal()
    try:
        project = db.query(Project).filter_by(id=project_id).first()
        if not project:
            return

        raw_posts = search_reddit(project.drug_name, limit=20)
        new_count = 0

        for raw in raw_posts:
            existing = db.query(Post).filter_by(source_post_id=raw.get("id", "")).first()
            if existing:
                continue

            nlp_result = process_post(raw["content"], raw.get("author", ""))
            posted_at = datetime.fromisoformat(raw["posted_at"]) if raw.get("posted_at") else datetime.utcnow()

            post = Post(
                project_id=project.id,
                source=raw.get("source", "reddit"),
                source_post_id=raw.get("id", f"crawl_{project_id}_{new_count}"),
                raw_content=raw["content"],
                anonymized_content=nlp_result["anonymized_content"],
                author_hash=nlp_result["author_hash"],
                url=raw.get("url", ""),
                posted_at=posted_at,
                extracted_adrs=nlp_result["extracted_adrs"],
                confidence_score=nlp_result["confidence_score"],
                is_first_person=nlp_result["is_first_person"],
                pii_detected=nlp_result["pii_detected"],
                location=raw.get("location"),
                subreddit=raw.get("subreddit"),
                is_processed=True,
            )
            db.add(post)
            new_count += 1

        db.flush()
        _update_signals(db, project)
        db.commit()
    finally:
        db.close()


def _update_signals(db: Session, project: Project):
    posts = db.query(Post).filter_by(project_id=project.id, is_processed=True).all()
    project.total_posts = len(posts)

    adr_counts: Dict[str, Dict] = {}
    for post in posts:
        if not post.is_first_person or post.confidence_score < 0.3:
            continue
        for adr in (post.extracted_adrs or []):
            term = adr["term"] if isinstance(adr, dict) else adr
            category = adr.get("category", "general") if isinstance(adr, dict) else "general"
            if term not in adr_counts:
                adr_counts[term] = {"count": 0, "category": category, "posts": [], "locations": set(), "confidences": []}
            adr_counts[term]["count"] += 1
            adr_counts[term]["posts"].append(post.id)
            adr_counts[term]["confidences"].append(post.confidence_score)
            if post.location:
                adr_counts[term]["locations"].add(post.location)

    for adr_term, data in adr_counts.items():
        if data["count"] < 1:
            continue

        label_result = compare_signal_to_label(project.drug_name, adr_term, data["count"])
        prr_result = calculate_prr(data["count"], len(posts), adr_term=adr_term)

        existing = db.query(Signal).filter_by(project_id=project.id, adr_term=adr_term).first()
        if existing:
            existing.report_count = data["count"]
            existing.prr_score = prr_result["prr"]
            existing.priority = label_result["priority"]
            existing.is_on_label = label_result["is_on_label"]
            existing.last_updated = datetime.utcnow()
            existing.locations = list(data["locations"])
        else:
            timeline = [{"week": f"Week {i+1}", "count": max(1, data["count"] - (3 - i))} for i in range(4)]
            avg_conf = sum(data["confidences"]) / max(len(data["confidences"]), 1)
            signal = Signal(
                project_id=project.id,
                drug_name=project.drug_name,
                adr_term=adr_term,
                adr_category=data["category"],
                report_count=data["count"],
                unique_sources=data["count"],
                prr_score=prr_result["prr"],
                confidence=avg_conf,
                is_on_label=label_result["is_on_label"],
                priority=label_result["priority"],
                source_posts=data["posts"],
                timeline=timeline,
                locations=list(data["locations"]),
                growth_rate=calculate_growth_rate(timeline),
                first_detected=datetime.utcnow() - timedelta(days=14),
            )
            db.add(signal)

    db.flush()
    project.total_signals = db.query(Signal).filter_by(project_id=project.id).count()


@app.get("/api/signals")
def list_all_signals(priority: Optional[str] = None, unlisted_only: bool = False, db: Session = Depends(get_db)):
    q = db.query(Signal)
    if priority:
        q = q.filter(Signal.priority == priority.upper())
    if unlisted_only:
        q = q.filter(Signal.is_on_label == False)
    signals = q.order_by(Signal.priority.desc(), Signal.report_count.desc()).limit(50).all()
    return [_signal_to_dict(s) for s in signals]


@app.get("/api/signals/{signal_id}")
def get_signal(signal_id: int, db: Session = Depends(get_db)):
    signal = db.query(Signal).filter_by(id=signal_id).first()
    if not signal:
        raise HTTPException(404, "Signal not found")

    source_posts = []
    if signal.source_posts:
        posts = db.query(Post).filter(Post.id.in_(signal.source_posts[:10])).all()
        source_posts = [_post_to_dict(p) for p in posts]

    return {**_signal_to_dict(signal), "source_posts": source_posts}


@app.post("/api/signals/{signal_id}/report")
def generate_report(signal_id: int, db: Session = Depends(get_db)):
    signal = db.query(Signal).filter_by(id=signal_id).first()
    if not signal:
        raise HTTPException(404, "Signal not found")

    project = db.query(Project).filter_by(id=signal.project_id).first()
    label_info = get_drug_label(signal.drug_name)

    posts = []
    if signal.source_posts:
        post_objs = db.query(Post).filter(Post.id.in_(signal.source_posts[:5])).all()
        posts = [_post_to_dict(p) for p in post_objs]

    project_dict = {
        "name": project.name,
        "drug_class": label_info.get("drug_class", ""),
        "brand_names": label_info.get("brand_names", []),
        "cdsco_approval": label_info.get("cdsco_approval", ""),
    }
    signal_dict = _signal_to_dict(signal)

    report_content = generate_pv_report(signal_dict, project_dict, posts)

    report = Report(
        project_id=project.id,
        signal_id=signal.id,
        title=f"PV Signal Report: {signal.drug_name.upper()} — {signal.adr_term.upper()}",
        content=report_content,
        status="draft",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "title": report.title,
        "generated_at": report.generated_at,
        "content": report_content,
    }


@app.get("/api/posts/{project_id}")
def get_project_posts(project_id: int, limit: int = 20, db: Session = Depends(get_db)):
    posts = db.query(Post).filter_by(project_id=project_id).order_by(
        Post.confidence_score.desc()
    ).limit(limit).all()
    return [_post_to_dict(p) for p in posts]


@app.get("/api/reports")
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.generated_at.desc()).all()
    return [{"id": r.id, "title": r.title, "status": r.status, "generated_at": r.generated_at} for r in reports]


@app.get("/api/reports/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter_by(id=report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    return {"id": report.id, "title": report.title, "status": report.status,
            "generated_at": report.generated_at, "content": report.content}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _signal_to_dict(s: Signal) -> Dict:
    return {
        "id": s.id,
        "project_id": s.project_id,
        "drug_name": s.drug_name,
        "adr_term": s.adr_term,
        "adr_category": s.adr_category,
        "first_detected": s.first_detected.isoformat() if s.first_detected else None,
        "last_updated": s.last_updated.isoformat() if s.last_updated else None,
        "report_count": s.report_count,
        "unique_sources": s.unique_sources,
        "prr_score": s.prr_score,
        "confidence": round(s.confidence, 2),
        "is_on_label": s.is_on_label,
        "priority": s.priority,
        "status": s.status,
        "growth_rate": s.growth_rate,
        "source_posts": s.source_posts or [],
        "timeline": s.timeline or [],
        "locations": s.locations or [],
    }


def _post_to_dict(p: Post) -> Dict:
    return {
        "id": p.id,
        "source": p.source,
        "subreddit": p.subreddit,
        "anonymized_content": p.anonymized_content,
        "url": p.url,
        "posted_at": p.posted_at.isoformat() if p.posted_at else None,
        "extracted_adrs": p.extracted_adrs or [],
        "confidence_score": p.confidence_score,
        "is_first_person": p.is_first_person,
        "pii_detected": p.pii_detected,
        "location": p.location,
    }
