from fastapi import FastAPI
from app.exceptions import register_exception_handlers
from app.database import engine, Base
from app.routers import auth, clients, properties, irrigation_systems, jobs, job_notes, reminders, calendar

app = FastAPI(
    title="Irrigation System API",
    description="CRM + maintenance system for irrigation technicians",
    version="1.0.0",
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(properties.router)
app.include_router(irrigation_systems.router)
app.include_router(jobs.router)
app.include_router(job_notes.router)
app.include_router(reminders.router)
app.include_router(calendar.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Import all models so they are registered with Base
        import app.models  # noqa
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Irrigation System API", "docs": "/docs"}
