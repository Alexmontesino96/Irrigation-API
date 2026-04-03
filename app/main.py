from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.exceptions import register_exception_handlers

from app.routers import auth, clients, properties, irrigation_systems, jobs, job_notes, reminders, calendar

app = FastAPI(
    title="Irrigation System API",
    description="CRM + maintenance system for irrigation technicians",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    import app.models  # noqa - register all models

@app.get("/")
async def root():
    return {"message": "Irrigation System API", "docs": "/docs"}
