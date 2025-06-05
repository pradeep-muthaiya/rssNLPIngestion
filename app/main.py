from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import themes, admin, ingest
from app.core.config import settings
from app.services.scheduler import scheduler
import multiprocessing
import atexit
import signal
from contextlib import asynccontextmanager

def cleanup_resources():
    """Clean up multiprocessing resources"""
    for process in multiprocessing.active_children():
        process.terminate()
        process.join()
    if hasattr(multiprocessing, 'resource_tracker'):
        # Reset the resource tracker instead of trying to clear it
        multiprocessing.resource_tracker._resource_tracker = multiprocessing.resource_tracker.ResourceTracker()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler.start()
    atexit.register(cleanup_resources)
    signal.signal(signal.SIGTERM, lambda s, f: cleanup_resources())
    signal.signal(signal.SIGINT, lambda s, f: cleanup_resources())
    yield
    # Shutdown
    scheduler.shutdown()
    cleanup_resources()

app = FastAPI(
    title="RSS NLP Ingestion Service",
    description="A service that ingests RSS feeds, extracts thesis statements, and analyzes themes",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(themes.router, prefix="/themes", tags=["themes"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"]) 