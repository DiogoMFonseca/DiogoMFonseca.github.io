# 📁 Project Structure

```
DiogoMFonseca.github.io/
│
├── 📄 main.py                          # Main orchestrator script
├── 📄 requirements.txt                 # Python dependencies
├── 📄 test_setup.py                    # Test script (validates setup)
├── 📄 README.md                        # Project documentation
├── 📄 context.md                       # Project context (Portuguese)
├── 📄 .gitignore                       # Git ignore rules
│
├── 📂 core/                            # Core functionality
│   ├── __init__.py
│   ├── driver.py                       # Selenium WebDriver setup (stealth mode)
│   └── database.py                     # SQLite operations + JSON export
│
├── 📂 scrapers/                        # Scraper modules
│   ├── __init__.py
│   └── teatro_aveirense.py            # Teatro Aveirense scraper
│   # 🔜 Future scrapers:
│   # ├── gretua.py
│   # ├── avenida_cafe.py
│   # ├── vic_aveiro.py
│   # └── ...
│
├── 📂 data/                            # Data storage (git-tracked)
│   ├── events.db                       # SQLite database (persistent history)
│   └── events.json                     # JSON export (API for frontend)
│
└── 📂 .github/
    └── workflows/
        └── scrape.yml                  # GitHub Actions workflow (daily execution)
```

## 📋 File Descriptions

### Root Files

**`main.py`**
- Main orchestrator that coordinates the entire scraping process
- Initializes database and Selenium driver
- Dynamically imports and runs scrapers
- Exports JSON for frontend consumption
- Handles errors gracefully (one failing scraper doesn't stop others)

**`requirements.txt`**
- Python dependencies:
  - `selenium` - Browser automation
  - `beautifulsoup4` - HTML parsing
  - `lxml` - HTML parser backend
  - `requests` - HTTP library

**`test_setup.py`**
- Validation script to test the setup without running Selenium
- Creates test events and validates database operations
- Good for quick testing during development

### Core Modules

**`core/driver.py`**
- Initializes Chrome WebDriver in headless mode
- Anti-bot detection configuration:
  - Human-like User-Agent
  - Disabled automation flags
  - Proper window sizing
  - JavaScript to hide webdriver property
- Optimized for Linux containers (GitHub Actions)

**`core/database.py`**
- `EventDatabase` class for SQLite operations
- Methods:
  - `upsert_event()` - Insert or update event (prevents duplicates by URL)
  - `get_future_events()` - Retrieve events with future dates
  - `export_to_json()` - Export to JSON file for frontend
  - `get_stats()` - Database statistics
- Event deduplication using URL-based hashing

### Scrapers

**`scrapers/teatro_aveirense.py`**
- Scrapes Teatro Aveirense events
- Uses direct AJAX endpoint access
- Parses HTML with BeautifulSoup
- Extracts: title, date, location, URL, image
- Normalizes dates to ISO-8601 format
- Each scraper follows the same pattern:
  ```python
  def scrape(driver, db):
      # Scraping logic
      return events_count
  ```

### Data Directory

**`data/events.db`**
- SQLite database (persistent)
- Stores historical data
- Schema:
  - `id` - Unique hash based on URL
  - `title` - Event name
  - `start_date` - ISO-8601 datetime
  - `end_date` - ISO-8601 datetime (optional)
  - `location` - Venue name
  - `url` - Event page URL (unique constraint)
  - `image_url` - Event image
  - `source` - Scraper source name
  - `tags` - JSON array of tags
  - `scraped_at` - Last scrape timestamp
  - `created_at` - First insertion timestamp

**`data/events.json`**
- JSON export of future events
- Consumed by frontend (FullCalendar)
- Regenerated on each scraper run
- Array of event objects

### GitHub Actions

**`.github/workflows/scrape.yml`**
- Workflow configuration
- Schedule: Daily at 08:00 UTC (cron: '0 8 * * *')
- Can be triggered manually via GitHub UI
- Steps:
  1. Checkout code
  2. Setup Python 3.11
  3. Install Chrome + ChromeDriver
  4. Install Python dependencies
  5. Run `main.py`
  6. Commit & push changes (events.db, events.json, logs)
  7. Upload artifacts (for debugging)

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│  GitHub Actions (Daily at 08:00)                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Initialize Database (SQLite)                      │  │
│  │ 2. Initialize Selenium Driver (Chrome Headless)      │  │
│  │ 3. For each scraper in scrapers/:                    │  │
│  │    ├─> Load scraper module dynamically               │  │
│  │    ├─> Execute scrape(driver, db)                    │  │
│  │    ├─> Extract & normalize event data                │  │
│  │    └─> db.upsert_event() → events.db                 │  │
│  │ 4. Export future events → events.json                │  │
│  │ 5. git commit & push (update repo)                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────┐
        │  GitHub Repository (Updated)     │
        │  ├─ data/events.db               │
        │  └─ data/events.json  ◀──────────┼───┐
        └─────────────────────────────────┘    │
                                                │
                                        ┌───────┴────────┐
                                        │  GitHub Pages  │
                                        │  Frontend      │
                                        │  (fetch JSON)  │
                                        └────────────────┘
```

## 🚀 Adding a New Scraper

1. Create a new file in `scrapers/` (e.g., `scrapers/new_venue.py`)
2. Implement the `scrape(driver, db)` function
3. Extract and normalize event data
4. Call `db.upsert_event(event_data)` for each event
5. Add the module to `SCRAPERS` list in `main.py`:
   ```python
   SCRAPERS = [
       'scrapers.teatro_aveirense',
       'scrapers.new_venue',  # Add here
   ]
   ```

## 📊 Event Data Schema

```json
{
  "id": "abc123def456",
  "title": "Concert Example",
  "start_date": "2026-02-15T20:00:00",
  "end_date": null,
  "location": "Teatro Aveirense",
  "url": "https://example.com/event",
  "image_url": "https://example.com/image.jpg",
  "source": "Teatro Aveirense",
  "tags": ["Música", "Rock"],
  "scraped_at": "2026-02-01T08:00:00"
}
```

## 🧪 Testing

```bash
# Test without Selenium (validates imports and database)
python test_setup.py

# Run full scraper locally
python main.py

# Check logs
cat scraper.log
```

## 📝 Notes

- The `data/` directory is git-tracked (contains the output)
- Logs are in `scraper.log`
- GitHub Actions artifacts are retained for 7 days
- Each scraper runs independently (one failure doesn't stop others)
