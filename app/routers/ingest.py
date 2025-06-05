from fastapi import APIRouter, HTTPException
from typing import List
from app.services.feed_service import FeedService
from app.schemas import ProcessFeedsResponse, Post

router = APIRouter(
    prefix="/ingest",
    tags=["ingest"]
)

@router.post("/process-all", response_model=ProcessFeedsResponse)
async def process_all_feeds():
    """Process all configured RSS feeds."""
    feed_service = FeedService()
    try:
        posts = await feed_service.process_all_feeds()
        return ProcessFeedsResponse(posts=posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-feed/{feed_url:path}", response_model=ProcessFeedsResponse)
async def process_feed(feed_url: str):
    """Process a specific RSS feed."""
    feed_service = FeedService()
    try:
        posts = await feed_service.process_feed(feed_url)
        return ProcessFeedsResponse(posts=posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 