import uuid
import enum
from datetime import datetime, date

from sqlalchemy import String, Float, DateTime, Date, Text, ForeignKey, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class JobStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    INSTALLATION = "installation"
    INSPECTION = "inspection"
    WINTERIZATION = "winterization"
    SPRING_STARTUP = "spring_startup"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    property_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("properties.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_type: Mapped[str] = mapped_column(
        String(50), default=JobType.MAINTENANCE.value
    )
    status: Mapped[str] = mapped_column(
        String(50), default=JobStatus.SCHEDULED.value
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    reminder_days: Mapped[list | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    property = relationship("Property", back_populates="jobs")
    job_notes = relationship("JobNote", back_populates="job")
    reminders = relationship("Reminder", back_populates="job")
