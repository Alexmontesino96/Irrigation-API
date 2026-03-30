from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class CalendarEvent(BaseModel):
    id: str
    type: str  # "job" | "reminder"
    title: str
    date: date
    status: str
    job_type: Optional[str] = None  # solo para jobs
    property_id: str
    job_id: Optional[str] = None  # solo para reminders


class CalendarDay(BaseModel):
    date: date
    events: List[CalendarEvent]


class CalendarResponse(BaseModel):
    start: date
    end: date
    days: List[CalendarDay]
    total_events: int
