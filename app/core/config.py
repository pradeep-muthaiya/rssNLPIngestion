from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "RSS NLP Ingestion Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # SQLite configuration
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "rss_nlp.db")
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{SQLITE_DB_PATH}"
    
    RSS_FEEDS: List[str] = [
        "http://feeds.bbci.co.uk/news/technology/rss.xml",  # BBC Technology News
        "https://www.theverge.com/rss/index.xml",          # The Verge
        "https://techcrunch.com/feed/",                    # TechCrunch
        "https://feeds.arstechnica.com/arstechnica/index"  # Ars Technica
    ]
    
    SCHEDULE_INTERVAL_MINUTES: int = 60  # Default to checking feeds every hour
    
    # NLP Settings
    SIMILARITY_THRESHOLD: float = 0.5  # Lowered threshold for better theme connection
    MODEL_NAME: str = "all-MiniLM-L6-v2"  # Default sentence transformer model

settings = Settings() 