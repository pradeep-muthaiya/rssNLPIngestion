from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import themes, admin, ingest
from app.core.config import settings
from app.services.scheduler import scheduler

app = FastAPI(
    title="RSS NLP Ingestion Service",
    description="A service that ingests RSS feeds, extracts thesis statements, and analyzes themes",
    version="1.0.0"
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

@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown() 