from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class ThemeBase(BaseModel):
    name: str
    description: Optional[str] = None

class ThemeCreate(ThemeBase):
    pass

class Theme(ThemeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    theme_id: int
    thesis_text: str
    post_title: str
    post_url: str
    published_at: datetime
    ingested_at: datetime

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProcessFeedsResponse(BaseModel):
    posts: List[Post]

class ThemeWithPosts(Theme):
    posts: List[Post]

class RSSFeedBase(BaseModel):
    url: HttpUrl
    name: str
    description: Optional[str] = None

class RSSFeedCreate(RSSFeedBase):
    pass

class RSSFeed(RSSFeedBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConfigUpdate(BaseModel):
    similarity_threshold: Optional[float] = None
    max_themes: Optional[int] = None 