"""API routes for managing scheduled scans."""

import uuid
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from preemptcore.core.models import ScheduleConfig
from preemptcore.core.scheduler import add_job_to_scheduler, remove_job_from_scheduler
from preemptcore.storage.db import get_session
from preemptcore.storage.models_db import DBSchedule

router = APIRouter()


class ScheduleCreateRequest(BaseModel):
    target_type: Literal["repo", "endpoint"]
    target_value: str
    cron_expression: str
    client_name: str | None = None


@router.post("", response_model=ScheduleConfig)
async def create_schedule(
    req: ScheduleCreateRequest, session: Session = Depends(get_session)
) -> ScheduleConfig:
    """Create a new scheduled scan."""
    schedule_id = f"sched_{uuid.uuid4().hex[:12]}"
    now = datetime.now(UTC)
    
    db_schedule = DBSchedule(
        schedule_id=schedule_id,
        target_type=req.target_type,
        target_value=req.target_value,
        cron_expression=req.cron_expression,
        client_name=req.client_name,
        created_at=now,
        is_active=True,
    )
    session.add(db_schedule)
    session.commit()
    session.refresh(db_schedule)

    # Add to APScheduler
    add_job_to_scheduler(db_schedule)

    return ScheduleConfig(
        schedule_id=db_schedule.schedule_id,
        target_type=db_schedule.target_type,
        target_value=db_schedule.target_value,
        cron_expression=db_schedule.cron_expression,
        client_name=db_schedule.client_name,
        created_at=db_schedule.created_at,
        is_active=db_schedule.is_active,
    )


@router.get("", response_model=list[ScheduleConfig])
async def list_schedules(session: Session = Depends(get_session)) -> list[ScheduleConfig]:
    """List all scheduled scans."""
    results = session.exec(select(DBSchedule).order_by(DBSchedule.created_at.desc())).all() # type: ignore
    
    return [
        ScheduleConfig(
            schedule_id=r.schedule_id,
            target_type=r.target_type,
            target_value=r.target_value,
            cron_expression=r.cron_expression,
            client_name=r.client_name,
            created_at=r.created_at,
            is_active=r.is_active,
        )
        for r in results
    ]


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str, session: Session = Depends(get_session)) -> dict[str, str]:
    """Delete and cancel a scheduled scan."""
    db_schedule = session.get(DBSchedule, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    session.delete(db_schedule)
    session.commit()

    remove_job_from_scheduler(schedule_id)
    return {"status": "deleted", "schedule_id": schedule_id}
