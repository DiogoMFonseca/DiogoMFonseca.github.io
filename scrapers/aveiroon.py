"""
AveiroOn scraper module.
"""

import logging
import re
import time
from datetime import datetime
from typing import Dict, Optional
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

SOURCE_NAME = "AveiroOn"
AGENDA_URL = "https://aveiroon.cm-aveiro.pt/eventos/"
BASE_URL = "https://aveiroon.cm-aveiro.pt"

# Meses em Inglês e Português para garantir
MONTHS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
    'fev': 2, 'abr': 4, 'mai': 5, 'ago': 8, 'set': 9, 'out': 10, 'dez': 12
}


def scrape(driver, db):
    logger.info(f"Starting scraper: {SOURCE_NAME}")
    events_count = 0

    try:
        logger.info(f"Navigating to: {AGENDA_URL}")
        driver.get(AGENDA_URL)

        # Esperar que o carrossel desktop carregue
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".display-today-events.intro"))
            )
            time.sleep(3)
        except Exception:
            logger.warning("Timeout waiting for desktop events container.")

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # ✅ Procura APENAS o contentor desktop (tem classe "intro")
        container = soup.select_one('.display-today-events.intro')

        if not container:
            logger.error("Container desktop '.display-today-events.intro' não encontrado!")
            return 0

        # Procuramos os eventos apenas DENTRO desse contentor desktop
        event_items = container.find_all('div', class_='today-event')
        logger.info(f"Found {len(event_items)} unique event items (desktop only)")

        for item in event_items:
            try:
                event_data = _parse_event_item(item)

                # Validação: Só guardamos se tiver título e data válida
                if event_data and event_data['title'] and event_data['start_date']:
                    logger.debug(f"Processando: {event_data['title']} -> {event_data['start_date']}")
                    db.upsert_event(event_data)
                    events_count += 1
                else:
                    if event_data:
                        logger.debug(f"Ignorado (sem data válida): {event_data.get('title')}")

            except Exception as e:
                logger.error(f"Error parsing item: {e}")
                continue

        logger.info(f"{SOURCE_NAME}: Successfully scraped {events_count} events")
        return events_count

    except Exception as e:
        logger.error(f"Error scraping {SOURCE_NAME}: {e}", exc_info=True)
        return events_count


def _parse_event_item(item) -> Optional[Dict]:
    title_tag = item.find('p', class_='title-today-event')
    if not title_tag: return None
    title = title_tag.get_text(strip=True)

    # Parsing da Data
    date_div = item.find('div', class_='date-today-event')
    start_date = None
    if date_div:
        date_p = date_div.find('p')
        if date_p:
            start_date = _parse_aveiroon_date(date_p.get_text(strip=True))

    # Link
    link_tag = item.find('a', class_='today-event-link', href=True)
    url = BASE_URL
    if link_tag:
        href = link_tag['href']
        url = href if href.startswith('http') else BASE_URL + href

    # Imagem
    img_wrapper = item.find('div', class_='image-today-event')
    image_url = None
    if img_wrapper:
        img_tag = img_wrapper.find('img')
        if img_tag:
            src = img_tag.get('data-lazy-src') or img_tag.get('src')
            if src and "data:image" not in src:
                image_url = src if src.startswith('http') else BASE_URL + src

    # Tags
    tags = [SOURCE_NAME]
    cat_link = item.find('a', class_='category-today-event')
    if cat_link:
        span = cat_link.find('span')
        if span: tags.append(span.get_text(strip=True))

    return {
        'title': title,
        'start_date': start_date,
        'end_date': None,
        'location': "Aveiro",
        'url': url,
        'image_url': image_url,
        'source': SOURCE_NAME,
        'tags': tags,
        'all_day': True
    }


def _parse_aveiroon_date(date_text: str) -> Optional[str]:
    """Parse date text ignoring fancy dashes."""
    if not date_text: return None

    clean_text = date_text.lower().strip()
    current_year = datetime.now().year

    # Regex: Digitos + Lixo (traços, espaços) + Letras
    match = re.search(r'(\d+)\s*[^0-9a-z]+\s*([a-z]+)', clean_text)

    if match:
        day, month_str = match.groups()
        month = MONTHS.get(month_str)

        if month:
            try:
                dt = datetime(current_year, month, int(day))
                # Ajuste de ano (ex: Evento em Jan, estamos em Dez)
                if datetime.now().month == 12 and month < 3:
                    dt = dt.replace(year=current_year + 1)

                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass

    # Log para saberes se falhou
    logger.warning(f"Falha ao ler data: '{clean_text}'")
    return None