"""
Database module for SQLite operations.
Handles event storage, deduplication, and JSON export.
"""

import sqlite3
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "events.db"
JSON_PATH = Path(__file__).parent.parent / "data" / "events.json"


class EventDatabase:
    """SQLite database manager for cultural events."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection and create tables if needed.

        Args:
            db_path: Optional custom database path
        """
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self.cursor = self.conn.cursor()
        logger.info(f"Database connected: {self.db_path}")

    def _create_tables(self):
        """Create events table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                location TEXT,
                url TEXT UNIQUE NOT NULL,
                image_url TEXT,
                source TEXT NOT NULL,
                tags TEXT,
                scraped_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        logger.info("Database tables initialized")

    @staticmethod
    def generate_event_id(url: str) -> str:
        """
        Generate unique event ID based on URL hash.

        Args:
            url: Event URL

        Returns:
            SHA256 hash of the URL (first 16 characters)
        """
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def upsert_event(self, event_data: Dict) -> bool:
        """
        Insert or update an event (prevents duplicates by URL).

        Args:
            event_data: Dictionary with event fields

        Returns:
            True if inserted, False if already exists
        """
        # Generate ID from URL
        event_id = self.generate_event_id(event_data['url'])

        # Add metadata
        event_data['id'] = event_id
        event_data['scraped_at'] = datetime.now().isoformat()

        # Convert tags list to JSON string
        if 'tags' in event_data and isinstance(event_data['tags'], list):
            event_data['tags'] = json.dumps(event_data['tags'])

        try:
            self.cursor.execute("""
                INSERT INTO events (
                    id, title, start_date, end_date, location, 
                    url, image_url, source, tags, scraped_at
                ) VALUES (
                    :id, :title, :start_date, :end_date, :location,
                    :url, :image_url, :source, :tags, :scraped_at
                )
                ON CONFLICT(url) DO UPDATE SET
                    title = excluded.title,
                    start_date = excluded.start_date,
                    end_date = excluded.end_date,
                    location = excluded.location,
                    image_url = excluded.image_url,
                    scraped_at = excluded.scraped_at
            """, event_data)
            self.conn.commit()

            # Check if it was an insert or update
            if self.cursor.rowcount > 0:
                logger.debug(f"Event upserted: {event_data.get('title', 'Unknown')}")
                return True
            return False

        except sqlite3.IntegrityError as e:
            logger.warning(f"Duplicate event skipped: {event_data.get('url', 'Unknown')} - {e}")
            return False
        except Exception as e:
            logger.error(f"Error inserting event: {e}")
            self.conn.rollback()
            return False

    def get_future_events(self) -> List[Dict]:
        """
        Retrieve all events with dates in the future or no date specified.

        Returns:
            List of event dictionaries
        """
        now = datetime.now().isoformat()

        self.cursor.execute("""
            SELECT id, title, start_date, end_date, location, 
                   url, image_url, source, tags, scraped_at
            FROM events
            WHERE start_date IS NULL OR start_date >= ?
            ORDER BY start_date ASC
        """, (now,))

        events = []
        for row in self.cursor.fetchall():
            event = dict(row)
            # Parse tags back to list
            if event['tags']:
                try:
                    event['tags'] = json.loads(event['tags'])
                except json.JSONDecodeError:
                    event['tags'] = []
            events.append(event)

        logger.info(f"Retrieved {len(events)} future events from database")
        return events

    def export_to_json(self, output_path: Optional[Path] = None) -> Path:
        """
        Export future events to JSON file for frontend consumption.

        Args:
            output_path: Optional custom output path

        Returns:
            Path to the exported JSON file
        """
        output_path = output_path or JSON_PATH
        output_path.parent.mkdir(parents=True, exist_ok=True)

        events = self.get_future_events()

        # Create JSON with metadata
        data = {
            'last_updated': datetime.now().isoformat(),
            'total_events': len(events),
            'events': events
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Exported {len(events)} events to {output_path}")
        return output_path

    def get_stats(self) -> Dict:
        """
        Get database statistics.

        Returns:
            Dictionary with stats
        """
        self.cursor.execute("SELECT COUNT(*) as total FROM events")
        total = self.cursor.fetchone()['total']

        self.cursor.execute("""
            SELECT source, COUNT(*) as count 
            FROM events 
            GROUP BY source
        """)
        by_source = {row['source']: row['count'] for row in self.cursor.fetchall()}

        return {
            'total_events': total,
            'by_source': by_source,
            'future_events': len(self.get_future_events())
        }

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
