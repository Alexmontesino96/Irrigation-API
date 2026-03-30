import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class JobNote(Base):
    __tablename__ = "job_notes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("jobs.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    job = relationship("Job", back_populates="job_notes")
