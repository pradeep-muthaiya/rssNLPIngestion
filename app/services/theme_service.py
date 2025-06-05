from typing import Optional, List, Tuple
from app.db.session import SessionLocal
from app.models import Theme, Post
from app.services.nlp_service import NLPService
from app.core.config import settings
from app.core.logging import logger
import re
from datetime import datetime, timedelta

class ThemeService:
    def __init__(self):
        self.nlp_service = NLPService()

    def clean_title(self, thesis: str) -> str:
        """Create a clean, meaningful title from the thesis."""
        # Remove URLs
        title = re.sub(r'http\S+|www.\S+', '', thesis)
        
        # Remove HTML tags
        title = re.sub(r'<[^>]+>', '', title)
        
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title)
        
        # Take first 100 characters or up to the last complete sentence
        title = title[:100]
        last_period = title.rfind('.')
        if last_period > 50:  # Only truncate at period if it's not too short
            title = title[:last_period + 1]
        
        return title.strip()

    def get_theme_candidates(self, thesis: str, db: SessionLocal) -> List[Tuple[Theme, float]]:
        """Get potential theme matches with their similarity scores."""
        candidates = []
        existing_themes = db.query(Theme).all()
        
        for theme in existing_themes:
            # Get all posts for this theme
            posts = db.query(Post).filter(Post.theme_id == theme.id).all()
            if not posts:
                continue
                
            # Calculate similarity with each post's thesis
            max_similarity = 0.0
            for post in posts:
                similarity = self.nlp_service.calculate_similarity(thesis, post.thesis_text)
                max_similarity = max(max_similarity, similarity)
            
            # Only consider themes with significant similarity
            if max_similarity >= settings.SIMILARITY_THRESHOLD:
                candidates.append((theme, max_similarity))
                logger.info(f"Found candidate theme '{theme.title}' with similarity score: {max_similarity:.2f}")
        
        # Sort by similarity score
        return sorted(candidates, key=lambda x: x[1], reverse=True)

    def find_or_create_theme(self, thesis: str) -> Theme:
        """Find an existing theme or create a new one based on thesis similarity."""
        db = SessionLocal()
        try:
            # Get potential theme matches
            candidates = self.get_theme_candidates(thesis, db)
            
            if candidates:
                # Get the best matching theme
                best_theme, similarity = candidates[0]
                logger.info(f"Selected best matching theme '{best_theme.title}' with similarity score: {similarity:.2f}")
                
                # If we have multiple good candidates, consider merging them
                if len(candidates) > 1 and candidates[1][1] >= settings.SIMILARITY_THRESHOLD:
                    # Get the second best match
                    second_theme, second_similarity = candidates[1]
                    
                    # If the second theme is very similar to the first, merge them
                    if second_similarity >= settings.SIMILARITY_THRESHOLD + 0.1:  # Slightly higher threshold for merging
                        logger.info(f"Merging themes '{second_theme.title}' into '{best_theme.title}' due to high similarity: {second_similarity:.2f}")
                        # Move all posts from second theme to first theme
                        posts_to_move = db.query(Post).filter(Post.theme_id == second_theme.id).all()
                        for post in posts_to_move:
                            post.theme_id = best_theme.id
                        
                        # Update the first theme's title if it's older
                        if best_theme.created_at > second_theme.created_at:
                            best_theme.title = self.clean_title(thesis)
                            logger.info(f"Updated theme title to: {best_theme.title}")
                        
                        # Delete the second theme
                        db.delete(second_theme)
                        db.commit()
                        logger.info(f"Deleted merged theme (ID: {second_theme.id})")
                
                return best_theme

            # Create new theme if no similar theme found
            clean_title = self.clean_title(thesis)
            new_theme = Theme(title=clean_title)
            db.add(new_theme)
            db.commit()
            db.refresh(new_theme)
            logger.info(f"Created new theme: '{clean_title}' (ID: {new_theme.id})")
            return new_theme

        finally:
            db.close()

    def get_theme_timeline(self, theme_id: int) -> Optional[dict]:
        """Get a timeline view of all posts for a theme."""
        db = SessionLocal()
        try:
            theme = db.query(Theme).filter(Theme.id == theme_id).first()
            if not theme:
                logger.warning(f"Theme not found with ID: {theme_id}")
                return None

            posts = db.query(Post).filter(Post.theme_id == theme_id).order_by(Post.published_at).all()
            logger.info(f"Retrieved {len(posts)} posts for theme '{theme.title}' (ID: {theme_id})")
            
            return {
                "theme_id": theme.id,
                "title": theme.title,
                "posts": [
                    {
                        "id": post.id,
                        "url": post.post_url,
                        "title": post.post_title,
                        "thesis": post.thesis_text,
                        "published_at": post.published_at.isoformat()
                    }
                    for post in posts
                ]
            }
        finally:
            db.close()

    def get_all_themes(self) -> list:
        """Get all themes with post counts."""
        db = SessionLocal()
        try:
            themes = db.query(Theme).all()
            theme_data = [
                {
                    "id": theme.id,
                    "title": theme.title,
                    "post_count": len(theme.posts)
                }
                for theme in themes
            ]
            logger.info(f"Retrieved {len(theme_data)} themes with post counts")
            return theme_data
        finally:
            db.close() 