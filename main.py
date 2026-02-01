"""
Aveiro Cultural Events Aggregator - Main Orchestrator
Runs web scrapers, stores events in SQLite, and exports JSON for frontend.
"""

import sys
import logging
import importlib
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.driver import initialize_driver, close_driver
from core.database import EventDatabase


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log')
    ]
)
logger = logging.getLogger(__name__)


# List of scraper modules to run
SCRAPERS = [
    'scrapers.teatro_aveirense',
    'scrapers.aveiroon',
    'scrapers.gretua',
    # 'scrapers.avenida_cafe',
]


def main():
    """Main orchestrator function."""
    logger.info("=" * 80)
    logger.info("Starting Aveiro Cultural Events Aggregator")
    logger.info(f"Execution time: {datetime.now().isoformat()}")
    logger.info("=" * 80)

    driver = None
    db = None
    total_events = 0
    scrapers_success = 0
    scrapers_failed = 0

    try:
        # Initialize database
        logger.info("Initializing database...")
        db = EventDatabase()

        # Show initial stats
        stats = db.get_stats()
        logger.info(f"Database stats: {stats}")

        # Initialize Selenium driver
        driver = initialize_driver()

        # Run each scraper
        for scraper_module_name in SCRAPERS:
            try:
                logger.info(f"\n{'=' * 60}")
                logger.info(f"Running scraper: {scraper_module_name}")
                logger.info('=' * 60)

                # Dynamically import the scraper module
                scraper_module = importlib.import_module(scraper_module_name)

                # Execute the scraper's scrape() function
                events_count = scraper_module.scrape(driver, db)
                total_events += events_count
                scrapers_success += 1

                logger.info(f"✓ {scraper_module_name}: {events_count} events scraped")

            except Exception as e:
                scrapers_failed += 1
                logger.error(f"✗ Error in scraper {scraper_module_name}: {e}", exc_info=True)
                continue

        # Export to JSON
        logger.info("\n" + "=" * 60)
        logger.info("Exporting data to JSON...")
        json_path = db.export_to_json()
        logger.info(f"✓ JSON exported to: {json_path}")

        # Final statistics
        logger.info("\n" + "=" * 80)
        logger.info("EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Scrapers executed: {scrapers_success + scrapers_failed}")
        logger.info(f"Scrapers successful: {scrapers_success}")
        logger.info(f"Scrapers failed: {scrapers_failed}")
        logger.info(f"Total events scraped: {total_events}")

        final_stats = db.get_stats()
        logger.info(f"Total events in database: {final_stats['total_events']}")
        logger.info(f"Future events: {final_stats['future_events']}")
        logger.info(f"Events by source: {final_stats['by_source']}")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"Critical error in main execution: {e}", exc_info=True)
        return 1

    finally:
        # Cleanup
        if driver:
            close_driver(driver)
        if db:
            db.close()
        logger.info("Execution completed\n")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

