"""
GrETUA (Viral Agenda) scraper module.
Scrapes events from Viral Agenda parsing the specific HTML structure.
Stops scraping when 'Past Events' section is reached.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Optional
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

SOURCE_NAME = "GrETUA"
AGENDA_URL = "https://www.viralagenda.com/pt/p/GrETUA.oficial"
BASE_URL = "https://www.viralagenda.com"

def scrape(driver, db):
    logger.info(f"Starting scraper: {SOURCE_NAME}")
    events_count = 0

    try:
        logger.info(f"Navigating to: {AGENDA_URL}")
        driver.get(AGENDA_URL)

        # Esperar que a lista de eventos carregue
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "viral-events"))
            )
            time.sleep(2)
        except Exception:
            logger.warning("Timeout waiting for #viral-events container.")

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Encontrar a lista principal (ul)
        ul_list = soup.find('ul', id='viral-events')

        if not ul_list:
            logger.error("Container '#viral-events' não encontrado!")
            return 0

        # Encontrar todos os items da lista (eventos, anúncios, passados)
        # Usamos recursive=False para garantir que são filhos diretos
        list_items = ul_list.find_all('li', recursive=False)
        logger.info(f"Found {len(list_items)} list items to process")

        for item in list_items:
            # 1. STOP CONDITION: Verificar se chegámos aos eventos passados
            classes = item.get('class', [])
            if 'viral-event-past' in classes:
                logger.info("🛑 Marcador 'Passados' encontrado. A parar o scraper.")
                break

            # 2. Ignorar Anúncios ou itens que não sejam eventos
            if 'viral-item-ads' in classes or 'viral-event' not in classes:
                continue

            try:
                event_data = _parse_event_item(item)

                # Validação: Só guardamos se tiver Título e Data
                if event_data and event_data['title'] and event_data['start_date']:
                    logger.debug(f"Processando: {event_data['title']} -> {event_data['start_date']}")
                    db.upsert_event(event_data)
                    events_count += 1
                else:
                    if event_data:
                        logger.debug(f"Ignorado (dados incompletos): {event_data.get('title')}")

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
    Parses a single 'li.viral-event' item.
    """
    # 1. DATA (O site fornece data-date-start="2026-02-02T21:00:00+00:00")
    # Isto é perfeito, não precisamos de regex.
    iso_date = item.get('data-date-start')
    start_date = None
    if iso_date:
        # Extrair apenas a parte YYYY-MM-DD
        try:
            start_date = iso_date.split('T')[0]
        except Exception:
            start_date = None

    # 2. TÍTULO
    # Estrutura: <div class="viral-event-title"><a><span>Título</span></a></div>
    title_div = item.find('div', class_='viral-event-title')
    title = "Sem título"
    if title_div:
        title = title_div.get_text(strip=True)

    # 3. LINK
    # O site fornece data-url="/pt/events/..."
    rel_url = item.get('data-url')
    url = BASE_URL # Fallback
    if rel_url:
        url = BASE_URL + rel_url if rel_url.startswith('/') else rel_url

    # 4. IMAGEM
    # Estrutura: <div class="viral-event-image" data-img="...">
    img_div = item.find('div', class_='viral-event-image')
    image_url = None
    if img_div:
        image_url = img_div.get('data-img')

    # 5. CATEGORIA (Tags)
    tags = [SOURCE_NAME]
    # Tenta encontrar a caixa da categoria
    cat_box = item.find('div', class_='viral-event-box-cat')
    if cat_box:
        cat_link = cat_box.find('a')
        if cat_link:
            tags.append(cat_link.get_text(strip=True))

    # 6. LOCALIZAÇÃO
    # Assumimos GrETUA pois estamos na página deles, mas podemos tentar extrair específico
    location = "GrETUA"
    place_box = item.find('a', class_='viral-event-place')
    if place_box:
        place_text = place_box.get_text(strip=True)
        if place_text:
            location = place_text

    return {
        'title': title,
        'start_date': start_date,
        'end_date': None, # O site tem data-date-end, mas para lista simples usamos start
        'location': location,
        'url': url,
        'image_url': image_url,
        'source': SOURCE_NAME,
        'tags': tags,
        'all_day': False # Viral agenda tem horas, mas o nosso calendário mostra tudo em dia
    }