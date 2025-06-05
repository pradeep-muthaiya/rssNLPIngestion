import feedparser
from datetime import datetime
from typing import List, Dict
import re
from bs4 import BeautifulSoup
from app.core.config import settings
from app.services.nlp_service import NLPService
from app.services.theme_service import ThemeService
from app.db.session import SessionLocal
from app.models import Post
from app.core.logging import logger

class FeedService:
    def __init__(self):
        self.nlp_service = NLPService()
        self.theme_service = ThemeService()

    def clean_content(self, content: str) -> str:
        """Clean HTML content and extract meaningful text."""
        # Remove HTML tags
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common HTML artifacts
        text = text.replace('Read full article', '')
        text = text.replace('Read more', '')
        
        return text.strip()

    async def process_feed(self, feed_url: str) -> List[Dict]:
        """Process a single RSS feed and return new posts."""
        logger.info(f"Starting to process feed: {feed_url}")
        feed = feedparser.parse(feed_url)
        new_posts = []
        skipped_posts = 0
        processed_posts = 0

        for entry in feed.entries:
            processed_posts += 1
            # Check if post already exists
            db = SessionLocal()
            existing_post = db.query(Post).filter(Post.post_url == entry.link).first()
            
            if existing_post:
                db.close()
                skipped_posts += 1
                continue

            # Extract and clean content
            content = entry.get('content', [{'value': ''}])[0]['value'] if 'content' in entry else entry.get('summary', '')
            cleaned_content = self.clean_content(content)
            
            # Extract thesis from cleaned content
            thesis_text = self.nlp_service.extract_thesis(cleaned_content)
            
            # Skip if no meaningful thesis was extracted
            if not thesis_text or len(thesis_text) < 20:  # Minimum length to ensure meaningful content
                db.close()
                skipped_posts += 1
                continue

            # Find or create theme
            theme = self.theme_service.find_or_create_theme(thesis_text)
            logger.info(f"Post '{entry.title}' assigned to theme: {theme.title} (ID: {theme.id})")

            # Create post with all required fields
            post = Post(
                theme_id=theme.id,
                thesis_text=thesis_text,
                post_title=entry.title,
                post_url=entry.link,
                content=cleaned_content,
                published_at=datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.utcnow(),
                ingested_at=datetime.utcnow()
            )

            db.add(post)
            db.commit()
            db.refresh(post)
            db.close()

            new_posts.append(post)
            logger.info(f"Successfully processed post: {entry.title}")

        logger.info(f"Feed processing complete for {feed_url}. Processed: {processed_posts}, New: {len(new_posts)}, Skipped: {skipped_posts}")
        return new_posts

    async def process_all_feeds(self) -> List[Dict]:
        """Process all configured RSS feeds."""
        logger.info(f"Starting to process all feeds. Total feeds: {len(settings.RSS_FEEDS)}")
        all_new_posts = []
        for feed_url in settings.RSS_FEEDS:
            try:
                new_posts = await self.process_feed(feed_url)
                all_new_posts.extend(new_posts)
            except Exception as e:
                logger.error(f"Error processing feed {feed_url}: {str(e)}")
        
        logger.info(f"Completed processing all feeds. Total new posts: {len(all_new_posts)}")
        return all_new_posts 