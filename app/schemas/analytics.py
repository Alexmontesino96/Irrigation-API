from pydantic import BaseModel
from typing import List


class FinancialSummary(BaseModel):
    revenue_this_month: float
    revenue_last_month: float
    revenue_change_pct: float
    expenses_this_month: float
    profit_margin: float
    outstanding: float
    jobs_completed: int


class MonthlyData(BaseModel):
    month: str
    revenue: float
    expenses: float


class RevenueByType(BaseModel):
    job_type: str
    total: float
    count: int
