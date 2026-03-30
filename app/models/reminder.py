import uuid
import enum
from datetime import datetime, date

from sqlalchemy import String, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class ReminderStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("jobs.id"), nullable=True
    )
    property_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("properties.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    remind_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default=ReminderStatus.PENDING.value
    )
    is_auto_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    job = relationship("Job", back_populates="reminders")
    property = relationship("Property")
