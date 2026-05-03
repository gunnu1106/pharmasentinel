"""
Background scheduler for automated crawling.
Runs crawl jobs based on project frequency settings (realtime / daily / weekly).

Usage:
    python scheduler.py          # runs standalone
    Or imported by main.py for integrated scheduling
"""
import time
import threading
from datetime import datetime, timedelta
from typing import Dict

from database import SessionLocal
from models import Project


FREQUENCY_INTERVALS: Dict[str, int] = {
    "realtime": 300,      # every 5 minutes
    "daily": 86400,       # every 24 hours
    "weekly": 604800,     # every 7 days
}

_scheduler_running = False
_scheduler_thread = None


class CrawlScheduler:
    def __init__(self):
        self.running = False
        self.last_run: Dict[int, datetime] = {}
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print(f"[Scheduler] Started at {datetime.utcnow().isoformat()}")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("[Scheduler] Stopped")

    def _run_loop(self):
        while self.running:
            try:
                self._check_and_run_jobs()
            except Exception as e:
                print(f"[Scheduler] Error: {e}")
            time.sleep(60)

    def _check_and_run_jobs(self):
        db = SessionLocal()
        try:
            projects = db.query(Project).filter_by(status="active").all()
            for project in projects:
                interval = FREQUENCY_INTERVALS.get(project.frequency, 86400)
                last = self.last_run.get(project.id)

                should_run = (
                    last is None or
                    (datetime.utcnow() - last).total_seconds() >= interval
                )

                if should_run:
                    print(f"[Scheduler] Running crawl for project {project.id} ({project.drug_name})")
                    self._run_crawl(project.id)
                    self.last_run[project.id] = datetime.utcnow()
        finally:
            db.close()

    def _run_crawl(self, project_id: int):
        from main import run_crawl
        thread = threading.Thread(target=run_crawl, args=(project_id,), daemon=True)
        thread.start()

    def get_status(self) -> Dict:
        db = SessionLocal()
        try:
            projects = db.query(Project).filter_by(status="active").all()
            jobs = []
            for p in projects:
                last = self.last_run.get(p.id)
                interval = FREQUENCY_INTERVALS.get(p.frequency, 86400)
                next_run = None
                if last:
                    next_run = (last + timedelta(seconds=interval)).isoformat()
                jobs.append({
                    "project_id": p.id,
                    "drug_name": p.drug_name,
                    "frequency": p.frequency,
                    "last_run": last.isoformat() if last else "never",
                    "next_run": next_run or "pending",
                })
            return {"running": self.running, "jobs": jobs}
        finally:
            db.close()


# Global scheduler instance
scheduler = CrawlScheduler()


if __name__ == "__main__":
    print("PharmaSentinel Scheduler")
    print("========================")
    scheduler.start()
    try:
        while True:
            time.sleep(30)
            status = scheduler.get_status()
            print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Jobs: {len(status['jobs'])}")
    except KeyboardInterrupt:
        scheduler.stop()
