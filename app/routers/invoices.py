from datetime import date
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceSummary
from app.schemas.common import PaginatedResponse
from app.services import invoice as invoice_service

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.post("", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    inv = await invoice_service.create_invoice(db, current_user.id, data.model_dump())
    return InvoiceResponse.from_invoice(inv)


@router.post("/from-job/{job_id}", response_model=InvoiceResponse, status_code=201)
async def create_invoice_from_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    inv = await invoice_service.create_invoice_from_job(db, current_user.id, job_id)
    return InvoiceResponse.from_invoice(inv)


@router.get("", response_model=PaginatedResponse[InvoiceResponse])
async def list_invoices(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    client_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    invoices, total = await invoice_service.get_invoices(
        db, current_user.id, page, size, status, client_id, date_from, date_to,
        sort_by=sort_by or "issue_date", sort_order=sort_order or "desc"
    )
    items = [InvoiceResponse.from_invoice(i) for i in invoices]
    return PaginatedResponse(
        items=items, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0
    )


@router.get("/summary", response_model=list[InvoiceSummary])
async def invoice_summary(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await invoice_service.get_invoice_summary(db, current_user.id, date_from, date_to)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    inv = await invoice_service.get_invoice(db, invoice_id, current_user.id)
    return InvoiceResponse.from_invoice(inv)


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    from app.services.invoice_pdf import generate_invoice_pdf
    inv = await invoice_service.get_invoice(db, invoice_id, current_user.id)
    pdf_bytes = generate_invoice_pdf(inv)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={inv.invoice_number}.pdf"},
    )


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    data: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    inv = await invoice_service.update_invoice(db, invoice_id, current_user.id, data.model_dump(exclude_unset=True))
    return InvoiceResponse.from_invoice(inv)


@router.delete("/{invoice_id}", status_code=204)
async def delete_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    await invoice_service.delete_invoice(db, invoice_id, current_user.id)
