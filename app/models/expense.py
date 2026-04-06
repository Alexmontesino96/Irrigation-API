import uuid
import enum
from datetime import datetime, date

from sqlalchemy import String, Numeric, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from app.database import Base


class ExpenseCategory(str, enum.Enum):
    MATERIALS = "materials"
    FUEL = "fuel"
    EQUIPMENT = "equipment"
    LABOR = "labor"
    OFFICE = "office"
    OTHER = "other"


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    job_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("jobs.id"), nullable=True
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    receipt_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
