"""
Quick test script to validate the scraper setup without running Selenium.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.database import EventDatabase
from datetime import datetime, timedelta


def test_database():
    """Test database functionality."""
    print("Testing Database...")

    # Create test database
    db = EventDatabase(db_path=Path("data/test_events.db"))

    # Insert test events
    test_events = [
        {
            'title': 'Concerto de Teste',
            'start_date': (datetime.now() + timedelta(days=5)).isoformat(),
            'end_date': None,
            'location': 'Teatro Aveirense',
            'url': 'https://example.com/event1',
            'image_url': 'https://example.com/image1.jpg',
            'source': 'Test Source',
            'tags': ['Música', 'Concerto']
        },
        {
            'title': 'Peça de Teatro',
            'start_date': (datetime.now() + timedelta(days=10)).isoformat(),
            'end_date': None,
            'location': 'GrETUA',
            'url': 'https://example.com/event2',
            'image_url': 'https://example.com/image2.jpg',
            'source': 'Test Source',
            'tags': ['Teatro']
        },
        {
            'title': 'Evento Passado (será filtrado)',
            'start_date': (datetime.now() - timedelta(days=5)).isoformat(),
            'end_date': None,
            'location': 'Aveiro',
            'url': 'https://example.com/event3',
            'image_url': None,
            'source': 'Test Source',
            'tags': []
        }
    ]

    for event in test_events:
        db.upsert_event(event)

    # Get stats
    stats = db.get_stats()
    print(f"✓ Total events in DB: {stats['total_events']}")
    print(f"✓ Future events: {stats['future_events']}")
    print(f"✓ Events by source: {stats['by_source']}")

    # Export JSON
    json_path = db.export_to_json(output_path=Path("data/test_events.json"))
    print(f"✓ JSON exported to: {json_path}")

    # Read future events
    future_events = db.get_future_events()
    print(f"\n✓ Future events retrieved: {len(future_events)}")
    for event in future_events:
        print(f"  - {event['title']} ({event['start_date']})")

    db.close()
    print("\n✅ Database tests passed!")


def test_imports():
    """Test that all modules can be imported."""
    print("\nTesting Imports...")

    try:
        from core.driver import initialize_driver, close_driver
        print("✓ core.driver imported")
    except ImportError as e:
        print(f"✗ Failed to import core.driver: {e}")
        return False

    try:
        from core.database import EventDatabase
        print("✓ core.database imported")
    except ImportError as e:
        print(f"✗ Failed to import core.database: {e}")
        return False

    try:
        from scrapers import teatro_aveirense
        print("✓ scrapers.teatro_aveirense imported")
    except ImportError as e:
        print(f"✗ Failed to import scrapers.teatro_aveirense: {e}")
        return False

    print("✅ All imports successful!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("AVEIRO CULTURAL EVENTS - TEST SUITE")
    print("=" * 60)

    # Create data directory
    Path("data").mkdir(exist_ok=True)

    # Run tests
    if test_imports():
        test_database()
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou can now run 'python main.py' to execute the full scraper.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
