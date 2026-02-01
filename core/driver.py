"""
Core driver module for Selenium WebDriver initialization.
Configures Chrome in headless mode with stealth options to avoid bot detection.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging

logger = logging.getLogger(__name__)


def initialize_driver():
    """
    Initialize Chrome WebDriver with stealth configuration for Linux containers.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    logger.info("Initializing Chrome WebDriver...")

    chrome_options = Options()

    # Headless mode for Linux container
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    # Window size (important for rendering)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")

    # Stealth options to avoid bot detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Human-like User Agent
    user_agent = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument(f"user-agent={user_agent}")

    # Additional privacy options
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")

    # Initialize driver
    driver = webdriver.Chrome(options=chrome_options)

    # Remove webdriver property to avoid detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Set page load timeout
    driver.set_page_load_timeout(30)

    logger.info("Chrome WebDriver initialized successfully")
    return driver


def close_driver(driver):
    """
    Safely close the WebDriver instance.

    Args:
        driver: WebDriver instance to close
    """
    if driver:
        try:
            driver.quit()
            logger.info("Chrome WebDriver closed successfully")
        except Exception as e:
            logger.error(f"Error closing driver: {e}")
