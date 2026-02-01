"""
Teatro Aveirense scraper module.
Scrapes events from Teatro Aveirense parsing the specific HTML structure of /programacao.
"""

import logging
import re
import time
from datetime import datetime
from typing import Dict, Optional, Tuple
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

SOURCE_NAME = "Teatro Aveirense"
AGENDA_URL = "https://www.teatroaveirense.pt/pt/programacao/"
BASE_URL = "https://www.teatroaveirense.pt"

# Mapeamento de meses PT -> Int
MONTHS = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
    'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
    'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
}

def scrape(driver, db):
    logger.info(f"Starting scraper: {SOURCE_NAME}")
    events_count = 0

    try:
        logger.info(f"Navigating to: {AGENDA_URL}")
        driver.get(AGENDA_URL)

        # Esperar pelo container principal dos itens
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "programa_item"))
            )
            time.sleep(2) # Wait for images/dynamic content
        except Exception:
            logger.warning("Timeout waiting for .programa_item. Page structure might have changed.")

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # O HTML mostra que os itens são 'div.programa_item'
        event_items = soup.find_all('div', class_='programa_item')
        logger.info(f"Found {len(event_items)} event items")

        for item in event_items:
            try:
                event_data = _parse_event_item(item)
                if event_data and event_data['title']:
                    db.upsert_event(event_data)
                    events_count += 1
            except Exception as e:
                logger.error(f"Error parsing item: {e}")
                continue

        logger.info(f"{SOURCE_NAME}: Successfully scraped {events_count} events")
        return events_count

    except Exception as e:
        logger.error(f"Error scraping {SOURCE_NAME}: {e}", exc_info=True)
        return events_count


def _parse_event_item(item) -> Optional[Dict]:
    """
    Parses a specific .programa_item div based on the provided HTML structure.
    """
    # 1. TÍTULO E SUBTÍTULO
    h2 = item.find('h2')
    if not h2:
        return None

    subtitle_tag = h2.find('span')
    subtitle = ""
    if subtitle_tag:
        subtitle = subtitle_tag.get_text(strip=True)
        subtitle_tag.extract()

    title_text = h2.get_text(strip=True)
    full_title = f"{title_text} - {subtitle}" if subtitle else title_text

    # 2. DATA
    date_div = item.find('div', class_='data')
    start_date = None
    end_date = None

    if date_div:
        date_text = date_div.get_text(strip=True)
        start_date, end_date = _parse_portuguese_date_string(date_text)

    # 3. LINK
    link_tag = item.find('a', href=True)
    url = BASE_URL
    if link_tag:
        href = link_tag['href']
        url = BASE_URL + href if href.startswith('/') else href

    # 4. IMAGEM
    img_tag = item.find('img', src=True)
    image_url = None
    if img_tag:
        src = img_tag['src']
        image_url = BASE_URL + src if src.startswith('/') else src

    # 5. CATEGORIA (Tags)
    tags = [SOURCE_NAME]
    cat_div = item.find('div', class_='categoria')
    if cat_div:
        spans = cat_div.find_all('span')
        for span in spans:
            txt = span.get_text(strip=True)
            if txt and "Categoria" not in txt:
                tags.append(txt)

    # 6. LOCALIZAÇÃO
    location = "Teatro Aveirense"

    return {
        'title': full_title,
        'start_date': start_date,
        'end_date': end_date,
        'location': location,
        'url': url,
        'image_url': image_url,
        'source': SOURCE_NAME,
        'tags': tags,
        'all_day': True  # <--- NOVA FLAG IMPORTANTE
    }


def _parse_portuguese_date_string(date_text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parses complex Portuguese date strings into YYYY-MM-DD formats (No time).
    """
    if not date_text:
        return None, None

    date_text = date_text.lower().replace('.', ' ').strip()
    current_year = datetime.now().year

    # Helper para converter "02 fevereiro" em string YYYY-MM-DD
    def make_date(day, month_name, year):
        month = MONTHS.get(month_name)
        if not month:
            return None
        # ALTERAÇÃO AQUI: strftime('%Y-%m-%d') remove as horas T00:00:00
        return datetime(year, month, int(day)).strftime('%Y-%m-%d')

    try:
        # Caso 1: Intervalo meses diferentes "26 abril - 03 maio"
        match_diff_months = re.match(r'(\d+)\s+([a-zç]+)\s*-\s*(\d+)\s+([a-zç]+)', date_text)
        if match_diff_months:
            d1, m1, d2, m2 = match_diff_months.groups()
            return make_date(d1, m1, current_year), make_date(d2, m2, current_year)

        # Caso 2: Intervalo mesmo mês "13-14 março"
        match_same_month = re.match(r'(\d+)\s*-\s*(\d+)\s+([a-zç]+)', date_text)
        if match_same_month:
            d1, d2, m1 = match_same_month.groups()
            return make_date(d1, m1, current_year), make_date(d2, m1, current_year)

        # Caso 3: Data única "02 fevereiro"
        match_single = re.match(r'(\d+)\s+([a-zç]+)', date_text)
        if match_single:
            d1, m1 = match_single.groups()
            iso_date = make_date(d1, m1, current_year)
            return iso_date, None

    except Exception as e:
        logger.warning(f"Date parsing failed for '{date_text}': {e}")

    return None, None