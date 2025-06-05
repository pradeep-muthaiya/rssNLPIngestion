from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from app.core.config import settings
from app.services.feed_service import FeedService
import json
import os

router = APIRouter()
feed_service = FeedService()

class RSSFeed(BaseModel):
    url: HttpUrl

class ConfigUpdate(BaseModel):
    similarity_threshold: Optional[float] = None
    schedule_interval_minutes: Optional[int] = None
    model_name: Optional[str] = None

@router.post("/feeds", response_model=dict)
async def add_feed(feed: RSSFeed):
    """Add a new RSS feed to the configuration."""
    try:
        # Read current feeds
        current_feeds = settings.RSS_FEEDS
        
        # Check if feed already exists
        if str(feed.url) in current_feeds:
            raise HTTPException(status_code=400, detail="Feed already exists")
        
        # Add new feed
        current_feeds.append(str(feed.url))
        
        # Update settings
        settings.RSS_FEEDS = current_feeds
        
        # Save to .env file
        with open('.env', 'a') as f:
            f.write(f'\nRSS_FEEDS={json.dumps(current_feeds)}')
        
        return {"message": "Feed added successfully", "feed": str(feed.url)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feeds", response_model=List[str])
async def list_feeds():
    """List all configured RSS feeds."""
    return settings.RSS_FEEDS

@router.delete("/feeds/{feed_url:path}")
async def remove_feed(feed_url: str):
    """Remove an RSS feed from the configuration."""
    try:
        # Read current feeds
        current_feeds = settings.RSS_FEEDS
        
        # Remove feed if it exists
        if feed_url in current_feeds:
            current_feeds.remove(feed_url)
            settings.RSS_FEEDS = current_feeds
            
            # Update .env file
            with open('.env', 'a') as f:
                f.write(f'\nRSS_FEEDS={json.dumps(current_feeds)}')
            
            return {"message": "Feed removed successfully"}
        else:
            raise HTTPException(status_code=404, detail="Feed not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config", response_model=dict)
async def update_config(config: ConfigUpdate):
    """Update configuration settings."""
    try:
        updates = {}
        
        # Update similarity threshold if provided
        if config.similarity_threshold is not None:
            if not 0 <= config.similarity_threshold <= 1:
                raise HTTPException(status_code=400, detail="Similarity threshold must be between 0 and 1")
            settings.SIMILARITY_THRESHOLD = config.similarity_threshold
            updates["similarity_threshold"] = config.similarity_threshold
        
        # Update schedule interval if provided
        if config.schedule_interval_minutes is not None:
            if config.schedule_interval_minutes < 1:
                raise HTTPException(status_code=400, detail="Schedule interval must be at least 1 minute")
            settings.SCHEDULE_INTERVAL_MINUTES = config.schedule_interval_minutes
            updates["schedule_interval_minutes"] = config.schedule_interval_minutes
        
        # Update model name if provided
        if config.model_name is not None:
            settings.MODEL_NAME = config.model_name
            updates["model_name"] = config.model_name
        
        # Save to .env file
        with open('.env', 'a') as f:
            for key, value in updates.items():
                f.write(f'\n{key.upper()}={value}')
        
        return {
            "message": "Configuration updated successfully",
            "updates": updates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config", response_model=dict)
async def get_config():
    """Get current configuration settings."""
    return {
        "similarity_threshold": settings.SIMILARITY_THRESHOLD,
        "schedule_interval_minutes": settings.SCHEDULE_INTERVAL_MINUTES,
        "model_name": settings.MODEL_NAME
    } 