"""
SQLite-based web cache for offline browsing
"""
import sqlite3
import json
import time
import hashlib
from pathlib import Path
from typing import Optional, List, Dict
from jarvis.web.scraper import WebScraper
class WebCache:
    """Local web content cache with full-text search"""
    
    def __init__(self, db_path: str = "data/web_cache.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.scraper = WebScraper()
        
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database with FTS5"""
        with sqlite3.connect(self.db_path) as conn:
            # Main pages table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT,
                    content TEXT,
                    text TEXT,
                    fetched_at REAL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL
                )
            """)
            
            # FTS5 virtual table for search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                    title, text,
                    content='pages',
                    content_rowid='id'
                )
            """)
            
            # Triggers to keep FTS index in sync
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS pages_ai AFTER INSERT ON pages BEGIN
                    INSERT INTO pages_fts(rowid, title, text)
                    VALUES (new.id, new.title, new.text);
                END
            """)
            
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS pages_ad AFTER DELETE ON pages BEGIN
                    INSERT INTO pages_fts(pages_fts, rowid, title, text)
                    VALUES ('delete', old.id, old.title, old.text);
                END
            """)
            
            conn.commit()
    
    def cache_url(self, url: str) -> bool:
        """
        Fetch and cache a URL.
        
        Args:
            url: URL to cache
        
        Returns:
            True if successful
        """
        data = self.scraper.fetch(url)
        if not data:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO pages 
                (url, title, content, text, fetched_at, access_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, 0, ?)
            """, (
                data['url'],
                data['title'],
                data['content'],
                data['article_text'],
                data['fetched_at'],
                time.time()
            ))
            conn.commit()
        
        print(f"✅ Cached: {data['title']}")
        return True
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search cached pages.
        
        Args:
            query: Search query
            limit: Max results
        
        Returns:
            List of matching pages
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Use FTS5 for search
            cursor = conn.execute("""
                SELECT p.id, p.url, p.title, p.text, p.fetched_at
                FROM pages_fts fts
                JOIN pages p ON fts.rowid = p.id
                WHERE pages_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))
            
            results = [dict(row) for row in cursor.fetchall()]
            
            # Update access stats
            for result in results:
                conn.execute("""
                    UPDATE pages 
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE id = ?
                """, (time.time(), result['id']))
            
            conn.commit()
            
            return results
    
    def get(self, url: str) -> Optional[Dict]:
        """Get cached page by URL"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute(
                "SELECT * FROM pages WHERE url = ?", (url,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update access stats
                conn.execute("""
                    UPDATE pages 
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE id = ?
                """, (time.time(), row['id']))
                conn.commit()
                
                return dict(row)
            
            return None
    
    def list_cached(self, limit: int = 20) -> List[Dict]:
        """List all cached pages"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT url, title, fetched_at, access_count 
                FROM pages 
                ORDER BY last_accessed DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def clear_old(self, days: int = 30):
        """Clear pages older than specified days"""
        cutoff = time.time() - (days * 24 * 3600)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM pages WHERE fetched_at < ?",
                (cutoff,)
            )
            conn.commit()
            print(f"🗑️ Cleared {cursor.rowcount} old pages")
    
    def close(self):
        """Cleanup"""
        pass
