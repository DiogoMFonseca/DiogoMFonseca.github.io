# Aveiro Cultural Events Aggregator

🎭 Agregador de eventos culturais da cidade de Aveiro e arredores.

## 📋 Descrição

Este projeto recolhe automaticamente eventos culturais de várias fontes em Aveiro (teatros, cinemas, espaços culturais) e centraliza toda a informação numa plataforma única e acessível.

## 🏗️ Arquitetura

### Backend (Web Scraping)
- **Infraestrutura**: GitHub Actions (execução diária às 08:00)
- **Linguagem**: Python 3.11+
- **Browser Automation**: Selenium WebDriver (Chrome Headless)
- **Parsing**: BeautifulSoup4
- **Armazenamento**: SQLite (`data/events.db`)
- **API**: Ficheiro JSON estático (`data/events.json`)

### Frontend
- **Hosting**: GitHub Pages
- **Consumo**: Fetch direto ao `events.json`

## 📁 Estrutura do Projeto

```
.
├── main.py                      # Orquestrador principal
├── requirements.txt             # Dependências Python
├── core/
│   ├── __init__.py
│   ├── driver.py               # Configuração Selenium (stealth mode)
│   └── database.py             # Gestão SQLite + Export JSON
├── scrapers/
│   ├── __init__.py
│   └── teatro_aveirense.py     # Scraper Teatro Aveirense
├── data/
│   ├── events.db               # Base de dados SQLite
│   └── events.json             # Export para frontend
├── .github/
│   └── workflows/
│       └── scrape.yml          # GitHub Actions workflow
└── scraper.log                 # Logs de execução
```

## 🔧 Instalação Local

### Pré-requisitos
- Python 3.11+
- Google Chrome
- ChromeDriver

### Setup

```bash
# Clonar repositório
git clone https://github.com/DiogoMFonseca/DiogoMFonseca.github.io.git
cd DiogoMFonseca.github.io

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Criar diretório de dados
mkdir -p data

# Executar scraper
python main.py
```

## 🎯 Fontes de Dados

### ✅ Implementadas
- [x] **Teatro Aveirense** 
- [x] Câmara Municipal de Aveiro
- [x] GrETUA (Grupo Experimental de Teatro da UA)

### 🔜 Próximas Implementações
- [ ] Avenida Café-Concerto
- [ ] VIC // Aveiro Arts House
- [ ] Fábrica Centro Ciência Viva
- [ ] Museu de Aveiro

## 📊 Formato de Dados

Cada evento segue o seguinte schema:

```json
{
  "id": "hash_unico",
  "title": "Nome do Evento",
  "start_date": "2026-02-15T20:00:00",
  "end_date": null,
  "location": "Teatro Aveirense",
  "url": "https://...",
  "image_url": "https://...",
  "source": "Teatro Aveirense",
  "tags": ["Teatro", "Cultura"],
  "scraped_at": "2026-02-01T08:00:00"
}
```

## 🚀 GitHub Actions

O workflow `.github/workflows/scrape.yml`:
- Executa diariamente às 08:00 UTC
- Instala Chrome + ChromeDriver
- Executa scrapers
- Faz commit de resultados automaticamente
- Pode ser executado manualmente via GitHub UI

## 🛡️ Anti-Bot Detection

O scraper utiliza várias técnicas para evitar deteção:
- User-Agent realista
- Headers HTTP customizados
- Flags Chrome anti-automação desativadas
- JavaScript para ocultar propriedade `navigator.webdriver`

## 📝 Logs

Os logs são guardados em `scraper.log` e também são visíveis nos outputs do GitHub Actions.

## 🤝 Contribuir

Pull requests são bem-vindos! Para mudanças maiores, abra uma issue primeiro.

## ⚠️ Disclaimer (Aviso Legal)
Este projeto é desenvolvido para fins estritamente educativos e de divulgação cultural sem fins lucrativos.

Propriedade Intelectual: Todos os dados (títulos, imagens, descrições) pertencem às respetivas instituições e organizações culturais. Este projeto apenas indexa links públicos.

Responsabilidade: O autor não se responsabiliza por erros na informação, cancelamentos de eventos ou alterações nos sites de origem.

Remoção: Se é representante de alguma entidade e deseja que os seus eventos não apareçam aqui, por favor abra uma [Issue](https://github.com/DiogoMFonseca/DiogoMFonseca.github.io/issues) e a fonte será removida imediatamente.

## 📄 Licença

Distribuído sob a licença MIT. Veja o ficheiro LICENSE para mais detalhes. Basicamente: use por sua conta e risco.

## 👤 Autor

**Diogo Fonseca**
- GitHub: [@DiogoMFonseca](https://github.com/DiogoMFonseca)

---

Feito com ❤️ para a comunidade cultural de Aveiro
