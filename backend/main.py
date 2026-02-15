from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.database import Base, engine
from backend.routers import (
    projects,
    budget,
    schedule,
    permits,
    punchlist,
    daily_logs,
    documents,
    subcontractors,
    dashboard,
    uploads,
    chat,
    education,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import all models so tables are registered
    import backend.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    # Ensure upload directories exist
    for sub in ("photos", "documents", "exports"):
        (Path(__file__).parent / "static" / sub).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="BuildFlow",
    description="Construction management platform for homeowner general contractors",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded photos/documents
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Register all routers
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])
app.include_router(budget.router, prefix="/api/v1", tags=["budget"])
app.include_router(schedule.router, prefix="/api/v1", tags=["schedule"])
app.include_router(permits.router, prefix="/api/v1", tags=["permits"])
app.include_router(punchlist.router, prefix="/api/v1", tags=["punchlist"])
app.include_router(daily_logs.router, prefix="/api/v1", tags=["daily-logs"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(subcontractors.router, prefix="/api/v1", tags=["subcontractors"])
app.include_router(uploads.router, prefix="/api/v1", tags=["uploads"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(education.router, prefix="/api/v1", tags=["education"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "BuildFlow", "version": "0.1.0"}
