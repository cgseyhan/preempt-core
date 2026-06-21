"""Background task scheduling using APScheduler."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session, select

from preemptcore.scanners.endpoint_scanner import EndpointScanner
from preemptcore.scanners.repo_scanner import RepoScanner
from preemptcore.storage.db import engine
from preemptcore.storage.models_db import DBSchedule
from preemptcore.storage.repositories import ScanRepository

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def run_scheduled_scan(schedule_id: str) -> None:
    """Execute a scan based on the given schedule_id."""
    with Session(engine) as session:
        db_schedule = session.get(DBSchedule, schedule_id)
        if not db_schedule or not db_schedule.is_active:
            logger.info(f"Schedule {schedule_id} not found or inactive. Skipping.")
            return

        target_type = db_schedule.target_type
        target_value = db_schedule.target_value
        client_name = db_schedule.client_name
        
    logger.info(f"Running scheduled scan {schedule_id} for {target_type} {target_value}")

    try:
        # Perform scan
        from pathlib import Path
        if target_type == "repo":
            scanner = RepoScanner()
            result = scanner.scan(Path(target_value))
        elif target_type == "endpoint":
            scanner_ep = EndpointScanner()
            result = scanner_ep.scan(target_value)
        else:
            logger.error(f"Unknown target type: {target_type}")
            return
            
        # Calculate Score
        from preemptcore.core.scoring import calculate_score
        breakdown = calculate_score(result)
        result.q_score = breakdown.final_score
        result.readiness_label = breakdown.readiness_label

        # Update client_name
        if result and client_name:
            result.client_name = client_name
            
        # Save result
        with Session(engine) as session:
            repo = ScanRepository(session)
            repo.save_scan(result)
            logger.info(f"Successfully saved scan {result.scan_id} for schedule {schedule_id}")

    except Exception as e:
        logger.error(f"Scheduled scan {schedule_id} failed: {e}")


def init_scheduler() -> None:
    """Load all active schedules from the DB and add them to the scheduler."""
    with Session(engine) as session:
        schedules = session.exec(select(DBSchedule).where(DBSchedule.is_active)).all()
        for sched in schedules:
            add_job_to_scheduler(sched)


def add_job_to_scheduler(schedule: DBSchedule) -> None:
    """Add a single job to the APScheduler."""
    try:
        trigger = CronTrigger.from_crontab(schedule.cron_expression)
        scheduler.add_job(
            run_scheduled_scan,
            trigger=trigger,
            args=[schedule.schedule_id],
            id=schedule.schedule_id,
            replace_existing=True,
        )
        logger.info(f"Added job {schedule.schedule_id} with cron {schedule.cron_expression}")
    except ValueError as e:
        logger.error(f"Invalid cron expression for schedule {schedule.schedule_id}: {e}")


def remove_job_from_scheduler(schedule_id: str) -> None:
    """Remove a job from the APScheduler."""
    if scheduler.get_job(schedule_id):
        scheduler.remove_job(schedule_id)
        logger.info(f"Removed job {schedule_id}")
