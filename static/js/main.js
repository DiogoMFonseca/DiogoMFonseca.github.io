/**
 * Aveiro Cultural Events - Main JavaScript
 * Handles event loading, calendar rendering, and filtering
 */

// Configuration
const CONFIG = {
    dataUrl: 'data/events.json',  // Change to 'data/test_events.json' for testing
    testDataUrl: 'data/test_events.json'
};

// Global state
let allEvents = [];
let calendar = null;
let currentFilter = 'all';

// Source color mapping
const SOURCE_COLORS = {
    'Teatro Aveirense': '#e74c3c',
    'GrETUA': '#3498db',
    'Avenida Café': '#f39c12',
    'VIC Aveiro': '#9b59b6',
    'Test Source': '#27ae60',
    'default': '#95a5a6'
};

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing Aveiro Cultural Events...');

    // Try to load test data first, fallback to real data
    await loadEvents();

    // Initialize calendar
    initializeCalendar();

    // Render event list
    renderEventList();

    // Update statistics
    updateStatistics();

    // Setup filter buttons
    setupFilters();
});

/**
 * Load events from JSON file
 */
async function loadEvents() {
    try {
        // Try production data first (data/events.json)
        let response = await fetch(CONFIG.dataUrl);

        if (!response.ok) {
            // Fallback to test data
            console.log('Production data not found, trying test data...');
            response = await fetch(CONFIG.testDataUrl);
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        allEvents = await response.json();
        console.log(`Loaded ${allEvents.length} events from JSON`);

        // Update last update time
        if (allEvents.length > 0) {
            const latestScrape = allEvents.reduce((latest, event) => {
                const scrapeDate = new Date(event.scraped_at);
                return scrapeDate > latest ? scrapeDate : latest;
            }, new Date(0));

            document.getElementById('lastUpdate').innerHTML =
                `<small><i class="bi bi-clock-history"></i> Atualizado: ${formatDate(latestScrape, true)}</small>`;
        }

    } catch (error) {
        console.error('Error loading events:', error);
        document.getElementById('eventList').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                Erro ao carregar eventos. Por favor, tente novamente mais tarde.
            </div>
        `;
    }
}

/**
 * Initialize FullCalendar
 */
function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');

    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'pt',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listWeek'
        },
        buttonText: {
            today: 'Hoje',
            month: 'Mês',
            week: 'Semana',
            list: 'Lista'
        },
        events: getFilteredCalendarEvents(),
        eventClick: function(info) {
            showEventModal(info.event.extendedProps.eventData);
            info.jsEvent.preventDefault();
        },
        height: 'auto',
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        }
    });

    calendar.render();
}

/**
 * Get filtered events for calendar
 */
function getFilteredCalendarEvents() {
    const filtered = currentFilter === 'all'
        ? allEvents
        : allEvents.filter(e => normalizeSource(e.source) === currentFilter);

    return filtered.map(event => ({
        title: event.title,
        start: event.start_date,
        end: event.end_date,
        backgroundColor: SOURCE_COLORS[event.source] || SOURCE_COLORS.default,
        borderColor: SOURCE_COLORS[event.source] || SOURCE_COLORS.default,
        extendedProps: {
            eventData: event
        }
    }));
}

/**
 * Render event list
 */
function renderEventList() {
    const eventListEl = document.getElementById('eventList');

    const filtered = currentFilter === 'all'
        ? allEvents
        : allEvents.filter(e => normalizeSource(e.source) === currentFilter);

    if (filtered.length === 0) {
        eventListEl.innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle"></i>
                Nenhum evento encontrado.
            </div>
        `;
        return;
    }

    // Sort by date
    const sortedEvents = [...filtered].sort((a, b) => {
        const dateA = new Date(a.start_date);
        const dateB = new Date(b.start_date);
        return dateA - dateB;
    });

    eventListEl.innerHTML = sortedEvents.map(event => `
        <div class="event-card ${normalizeSource(event.source)}" onclick="showEventModal(${JSON.stringify(event).replace(/"/g, '&quot;')})">
            <div class="row">
                ${event.image_url ? `
                    <div class="col-auto">
                        <img src="${event.image_url}" alt="${event.title}" class="event-image" 
                             onerror="this.style.display='none'">
                    </div>
                ` : ''}
                <div class="col">
                    <div class="event-title">${event.title}</div>
                    <div class="event-meta">
                        <i class="bi bi-calendar-event"></i> ${formatDate(new Date(event.start_date))}
                        <br>
                        <i class="bi bi-geo-alt"></i> ${event.location || 'Local não especificado'}
                        <br>
                        <span class="badge bg-secondary source-badge">${event.source}</span>
                        ${event.tags && event.tags.length > 0 ? 
                            event.tags.map(tag => `<span class="badge bg-light text-dark source-badge">${tag}</span>`).join(' ')
                            : ''
                        }
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Show event details modal
 */
function showEventModal(event) {
    const modal = new bootstrap.Modal(document.getElementById('eventModal'));

    document.getElementById('modalTitle').textContent = event.title;
    document.getElementById('modalLink').href = event.url;

    const startDate = new Date(event.start_date);
    const endDate = event.end_date ? new Date(event.end_date) : null;

    document.getElementById('modalBody').innerHTML = `
        ${event.image_url ? `
            <img src="${event.image_url}" alt="${event.title}" class="img-fluid mb-3 rounded" 
                 onerror="this.style.display='none'">
        ` : ''}
        
        <div class="mb-3">
            <h6><i class="bi bi-calendar-event"></i> Data</h6>
            <p>${formatDate(startDate, true)}${endDate ? ` até ${formatDate(endDate, true)}` : ''}</p>
        </div>
        
        <div class="mb-3">
            <h6><i class="bi bi-geo-alt"></i> Local</h6>
            <p>${event.location || 'Não especificado'}</p>
        </div>
        
        <div class="mb-3">
            <h6><i class="bi bi-building"></i> Fonte</h6>
            <p><span class="badge" style="background-color: ${SOURCE_COLORS[event.source] || SOURCE_COLORS.default}">${event.source}</span></p>
        </div>
        
        ${event.tags && event.tags.length > 0 ? `
            <div class="mb-3">
                <h6><i class="bi bi-tags"></i> Categorias</h6>
                <p>${event.tags.map(tag => `<span class="badge bg-secondary">${tag}</span>`).join(' ')}</p>
            </div>
        ` : ''}
    `;

    modal.show();
}

/**
 * Update statistics
 */
function updateStatistics() {
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    // Total events
    document.getElementById('totalEvents').textContent = allEvents.length;

    // Events this month
    const thisMonth = allEvents.filter(event => {
        const eventDate = new Date(event.start_date);
        return eventDate.getMonth() === currentMonth && eventDate.getFullYear() === currentYear;
    }).length;
    document.getElementById('thisMonth').textContent = thisMonth;

    // Total sources
    const sources = new Set(allEvents.map(e => e.source));
    document.getElementById('totalSources').textContent = sources.size;

    // Next event
    const futureEvents = allEvents
        .filter(e => new Date(e.start_date) > now)
        .sort((a, b) => new Date(a.start_date) - new Date(b.start_date));

    if (futureEvents.length > 0) {
        const nextEventDate = new Date(futureEvents[0].start_date);
        const daysUntil = Math.ceil((nextEventDate - now) / (1000 * 60 * 60 * 24));
        document.getElementById('nextEvent').textContent = `${daysUntil}d`;
    } else {
        document.getElementById('nextEvent').textContent = '-';
    }
}

/**
 * Setup filter buttons
 */
function setupFilters() {
    const sources = [...new Set(allEvents.map(e => e.source))];
    const filterContainer = document.getElementById('filterButtons');

    sources.forEach(source => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-sm btn-outline-secondary filter-btn';
        btn.dataset.filter = normalizeSource(source);
        btn.innerHTML = `<i class="bi bi-building"></i> ${source}`;
        btn.addEventListener('click', () => setFilter(normalizeSource(source)));
        filterContainer.appendChild(btn);
    });

    // Setup filter button clicks
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

/**
 * Set active filter
 */
function setFilter(filter) {
    currentFilter = filter;

    // Update calendar
    if (calendar) {
        calendar.removeAllEvents();
        calendar.addEventSource(getFilteredCalendarEvents());
    }

    // Update event list
    renderEventList();
}

/**
 * Normalize source name for CSS class
 */
function normalizeSource(source) {
    return source.toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9-]/g, '');
}

/**
 * Format date to Portuguese locale
 */
function formatDate(date, includeTime = false) {
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };

    if (includeTime && date.getHours() !== 0) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }

    return date.toLocaleDateString('pt-PT', options);
}

// Make showEventModal available globally for onclick handlers
window.showEventModal = showEventModal;
