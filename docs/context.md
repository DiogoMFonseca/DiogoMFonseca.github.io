# Contexto do Projeto: Agregador Cultural de Aveiro

## 1. Visão e Objetivo
**Missão:** Centralizar a oferta cultural da cidade de Aveiro (e arredores) numa única plataforma acessível, combatendo a dispersão de informação e o "gatekeeping" involuntário causado pela multiplicidade de fontes (Facebook, Instagram, sites institucionais, agendas em papel).
**Público-alvo:** Residentes, estudantes (UA), ex-residentes e turistas.
**Ano Corrente:** 2026.

## 2. Arquitetura Técnica
O sistema funciona num modelo "Serverless" utilizando a infraestrutura gratuita do GitHub.

### Backend (Data Pipeline)
* **Infraestrutura:** GitHub Actions (Linux Runner).
* **Frequência:** Execução diária (Cron Job às 08:00).
* **Linguagem:** Python 3.13+.
* **Engine de Scraping:** * Selenium WebDriver (Chrome Headless) para navegação e renderização de JS.
    * BeautifulSoup4 para parsing de HTML estático quando possível.
* **Armazenamento:**
    * `events.db` (SQLite): Persistência de histórico e gestão de duplicados.
    * `events.json`: Ficheiro estático exportado no final de cada execução. É a "API" do frontend.

### Frontend
* **Hosting:** GitHub Pages.
* **Stack:** HTML5, CSS3, JavaScript (Vanilla ou Framework leve). Render de eventos com FullCalendar
* **Consumo de Dados:** Fetch direto ao ficheiro `events.json` gerado pelo backend.
* **Visualização:** FullCalendar (ou similar) para mostrar eventos.

## 3. Fontes de Dados (Mapeamento)

### Prioridade 1: Implementação Imediata
* **Teatro Aveirense**
    * *Tipo:* Institucional / Mainstream.
    * *Endpoint Descoberto:* `https://www.teatroaveirense.pt/include/ajax_functions.php?action=eventos&langid=1`
    * *Método:* GET (Requer headers 'X-Requested-With': 'XMLHttpRequest').
    * *Formato:* Retorna HTML cru (divs com classe `.item`).

### Prioridade 2: Próximos Scrapers
* **GrETUA (Grupo Experimental de Teatro da UA):** Cultura alternativa, cinema, concertos.
* **Avenida Café-Concerto:** Concertos, rock, jazz, poetry slam.
* **AveirOn:** Agregador local existente (fonte secundária para validação).
* **Viral Agenda (Aveiro):** Fonte generalista.
* **VIC // Aveiro Arts House:** Cinema documental, residências artísticas.
* **Câmara Municipal de Aveiro (Site/Agenda):** Eventos oficiais, feiras e mercados.

### Prioridade 3: Nichos e Workshops
* **Agora Aveiro:** Workshops sustentabilidade/intervenção cívica.
* **Fábrica Centro Ciência Viva:** Ciência e tecnologia.
* **Museu de Aveiro:** Exposições.

## 4. Estrutura de Dados Desejada
Cada evento recolhido deve ser normalizado para o seguinte esquema (JSON/DB):

```json
{
  "id": "hash_unico_baseado_url",
  "title": "Nome do Evento",
  "start_date": "ISO-8601 (YYYY-MM-DDTHH:MM:SS)",
  "end_date": "ISO-8601 (Opcional)",
  "location": "Local do evento",
  "url": "Link original",
  "image_url": "Link da imagem de capa",
  "source": "Nome da Fonte (ex: Teatro Aveirense)",
  "tags": ["Teatro", "Cinema", "Música"], 
  "scraped_at": "Data de recolha"
}
```

## 5. Notas de Implementação

* **Stealth Mode:** O scraper deve utilizar headers humanos e flags do Chrome para evitar bloqueios (anti-bot detection), visto que correrá em IPs de datacenter (GitHub/Azure).
* **Persistência:** O workflow do GitHub Actions deve incluir um passo final de `git commit & push` para atualizar a base de dados e o JSON no repositório.
