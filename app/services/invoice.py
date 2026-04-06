from datetime import date
from typing import Optional
from sqlalchemy import select, func, asc, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
from app.models.job import Job
from app.models.job_material import JobMaterial
from app.models.property import Property
from app.models.client import Client
from app.exceptions import NotFoundException, BadRequestException

_INVOICE_SORT_WHITELIST = {"invoice_number", "issue_date", "due_date", "total", "status", "created_at"}


async def _next_invoice_number(db: AsyncSession, owner_id: str) -> str:
    result = await db.execute(
        select(func.count()).select_from(Invoice).where(Invoice.owner_id == owner_id)
    )
    count = result.scalar() or 0
    return f"INV-{count + 1:03d}"


async def create_invoice(db: AsyncSession, owner_id: str, data: dict) -> Invoice:
    # Verify client ownership
    result = await db.execute(
        select(Client).where(Client.id == data["client_id"], Client.owner_id == owner_id)
    )
    if not result.scalar_one_or_none():
        raise NotFoundException("Client not found")

    items_data = data.pop("items", [])
    invoice_number = await _next_invoice_number(db, owner_id)

    # Calculate totals
    subtotal = sum(item["quantity"] * item["unit_price"] for item in items_data)
    tax_rate = data.get("tax_rate", 0)
    tax_amount = round(subtotal * tax_rate / 100, 2)
    total = round(subtotal + tax_amount, 2)

    invoice = Invoice(
        owner_id=owner_id,
        invoice_number=invoice_number,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total=total,
        **data,
    )
    db.add(invoice)
    await db.flush()

    for item_data in items_data:
        item_total = round(item_data["quantity"] * item_data["unit_price"], 2)
        item = InvoiceItem(
            invoice_id=invoice.id,
            total=item_total,
            **item_data,
        )
        db.add(item)

    await db.commit()
    await db.refresh(invoice)
    return await get_invoice(db, invoice.id, owner_id)


async def create_invoice_from_job(db: AsyncSession, owner_id: str, job_id: str) -> Invoice:
    # Get job with ownership check
    result = await db.execute(
        select(Job).join(Property).join(Client).where(
            Job.id == job_id, Client.owner_id == owner_id
        ).options(
            joinedload(Job.property).joinedload(Property.client),
            joinedload(Job.materials),
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Job not found")

    items_data = []
    # Add job service as first item
    if job.price:
        items_data.append({
            "description": job.title,
            "quantity": 1,
            "unit_price": float(job.price),
            "job_id": job.id,
        })

    # Add materials
    for mat in job.materials:
        items_data.append({
            "description": mat.name,
            "quantity": mat.quantity,
            "unit_price": float(mat.unit_cost),
            "job_id": job.id,
        })

    if not items_data:
        raise BadRequestException("Job has no price or materials to invoice")

    from datetime import timedelta
    today = date.today()
    return await create_invoice(db, owner_id, {
        "client_id": job.property.client.id,
        "issue_date": today,
        "due_date": today + timedelta(days=30),
        "tax_rate": 0,
        "items": items_data,
    })


async def get_invoices(
    db: AsyncSession,
    owner_id: str,
    page: int = 1,
    size: int = 20,
    status: Optional[str] = None,
    client_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort_by: str = "issue_date",
    sort_order: str = "desc",
) -> tuple[list[Invoice], int]:
    query = select(Invoice).where(Invoice.owner_id == owner_id).options(
        joinedload(Invoice.client), joinedload(Invoice.items)
    )
    count_query = select(func.count()).select_from(Invoice).where(Invoice.owner_id == owner_id)

    if status:
        query = query.where(Invoice.status == status)
        count_query = count_query.where(Invoice.status == status)
    if client_id:
        query = query.where(Invoice.client_id == client_id)
        count_query = count_query.where(Invoice.client_id == client_id)
    if date_from:
        query = query.where(Invoice.issue_date >= date_from)
        count_query = count_query.where(Invoice.issue_date >= date_from)
    if date_to:
        query = query.where(Invoice.issue_date <= date_to)
        count_query = count_query.where(Invoice.issue_date <= date_to)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    col = getattr(Invoice, sort_by) if sort_by in _INVOICE_SORT_WHITELIST else Invoice.issue_date
    order_fn = asc if sort_order == "asc" else desc
    query = query.order_by(order_fn(col)).offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    invoices = list(result.unique().scalars().all())
    return invoices, total


async def get_invoice(db: AsyncSession, invoice_id: str, owner_id: str) -> Invoice:
    result = await db.execute(
        select(Invoice).where(
            Invoice.id == invoice_id, Invoice.owner_id == owner_id
        ).options(joinedload(Invoice.client), joinedload(Invoice.items))
    )
    invoice = result.unique().scalar_one_or_none()
    if not invoice:
        raise NotFoundException("Invoice not found")
    return invoice


async def update_invoice(db: AsyncSession, invoice_id: str, owner_id: str, data: dict) -> Invoice:
    invoice = await get_invoice(db, invoice_id, owner_id)
    for key, value in data.items():
        if value is not None:
            setattr(invoice, key, value)
    await db.commit()
    await db.refresh(invoice)
    return await get_invoice(db, invoice_id, owner_id)


async def delete_invoice(db: AsyncSession, invoice_id: str, owner_id: str) -> None:
    invoice = await get_invoice(db, invoice_id, owner_id)
    if invoice.status != InvoiceStatus.DRAFT.value:
        raise BadRequestException("Only draft invoices can be deleted")
    await db.delete(invoice)
    await db.commit()


async def get_invoice_summary(
    db: AsyncSession,
    owner_id: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> list[dict]:
    query = (
        select(
            Invoice.status,
            func.sum(Invoice.total).label("total"),
            func.count().label("count"),
        )
        .where(Invoice.owner_id == owner_id)
        .group_by(Invoice.status)
    )
    if date_from:
        query = query.where(Invoice.issue_date >= date_from)
    if date_to:
        query = query.where(Invoice.issue_date <= date_to)

    result = await db.execute(query)
    rows = result.all()
    return [{"status": r.status, "total": float(r.total or 0), "count": r.count} for r in rows]
