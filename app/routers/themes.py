from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.theme_service import ThemeService
from typing import List, Dict

router = APIRouter()
theme_service = ThemeService()

@router.get("/", response_model=List[Dict])
async def list_themes():
    """List all themes with their post counts."""
    return theme_service.get_all_themes()

@router.get("/{theme_id}", response_model=Dict)
async def get_theme_timeline(theme_id: int):
    """Get a timeline view of all posts for a specific theme."""
    theme_data = theme_service.get_theme_timeline(theme_id)
    if not theme_data:
        raise HTTPException(status_code=404, detail="Theme not found")
    return theme_data 