import uuid
from datetime import datetime, date

from sqlalchemy import String, Integer, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class IrrigationSystem(Base):
    __tablename__ = "irrigation_systems"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    property_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("properties.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    system_type: Mapped[str] = mapped_column(String(50), nullable=False)
    zone_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    install_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    property = relationship("Property", back_populates="irrigation_systems")
