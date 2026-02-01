document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const filterContainer = document.getElementById('filterButtons');

    // Elementos de Estatística
    const statTotal = document.getElementById('totalEvents');
    const statMonth = document.getElementById('thisMonth');
    const statNext = document.getElementById('nextEventDays');

    // Inicializar o Calendário
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'pt',
        height: 'auto',        // Deixa o calendário crescer conforme necessário
        contentHeight: 'auto', // Garante que as células têm tamanho
        aspectRatio: 1.35,     // Mantém uma proporção agradável
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,listMonth'
        },
        buttonText: {
            today: 'Hoje',
            month: 'Mês',
            list: 'Lista'
        },
        eventClick: function (info) {
            showEventModal(info.event);
        },
        eventDidMount: function (info) {
            // Tooltip simples ao passar o rato
            info.el.title = info.event.title;
        }
    });

    calendar.render();

    // Carregar os dados
    fetch('data/events.json')
        .then(response => {
            if (!response.ok) throw new Error("Erro ao ler JSON");
            return response.json();
        })
        .then(data => {
            // 1. Esconder o Loading
            loadingSpinner.style.display = 'none';

            // 2. Preparar os eventos para o FullCalendar
            const events = data.map(event => ({
                id: event.id,
                title: event.title,
                start: event.start_date,
                end: event.end_date,
                url_original: event.url, // Guardamos o url original numa prop extra
                image_url: event.image_url,
                location: event.location,
                source: event.source,
                // Atribuir cor baseada na fonte
                classNames: ['evt-' + normalizeSource(event.source)]
            }));

            // 3. Adicionar ao calendário
            calendar.addEventSource(events);

            // 4. Gerar Botões de Filtro
            generateFilters(events, calendar);

            // 5. Atualizar Estatísticas do Rodapé
            updateStats(events);

            // 6. Atualizar data de "Last Update" no header
            document.getElementById('lastUpdate').innerHTML =
                `<i class="bi bi-check-circle-fill text-success"></i> Atualizado`;

        })
        .catch(error => {
            console.error('Erro:', error);
            loadingSpinner.innerHTML = `<div class="text-danger"><i class="bi bi-exclamation-triangle"></i> Erro ao carregar eventos.</div>`;
        });
});

/**
 * Função para normalizar o nome da fonte para usar no CSS
 * Ex: "Teatro Aveirense" -> "teatro"
 */
function normalizeSource(sourceName) {
    if (!sourceName) return 'default';
    const s = sourceName.toLowerCase();
    if (s.includes('teatro')) return 'teatro';
    if (s.includes('gretua')) return 'gretua';
    if (s.includes('avenida')) return 'avenida';
    if (s.includes('vic')) return 'vic';
    return 'default';
}

/**
 * Gera os botões de filtro no topo com base nas fontes existentes
 */
function generateFilters(events, calendar) {
    const sources = [...new Set(events.map(e => e.source))];
    const container = document.getElementById('filterButtons');

    // Limpar botões (mantendo o "Todos")
    // container.innerHTML = '<button class="btn filter-btn active" data-filter="all">Todos</button>';

    sources.forEach(source => {
        const btn = document.createElement('button');
        btn.className = 'btn filter-btn';
        btn.textContent = source;
        btn.onclick = () => {
            // Remover classe active de todos
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Filtrar calendário
            const allEvents = calendar.getEvents();
            allEvents.forEach(evt => {
                if (evt.extendedProps.source === source) {
                    evt.setProp('display', 'auto');
                } else {
                    evt.setProp('display', 'none');
                }
            });
        };
        container.appendChild(btn);
    });

    // Reativar o botão "Todos"
    const btnAll = container.querySelector('[data-filter="all"]');
    if (btnAll) {
        btnAll.onclick = () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btnAll.classList.add('active');

            calendar.getEvents().forEach(evt => evt.setProp('display', 'auto'));
        };
    }
}

/**
 * Calcula e atualiza os números no rodapé
 */
function updateStats(events) {
    // 1. Total
    document.getElementById('totalEvents').textContent = events.length;

    // 2. Este Mês
    const now = new Date();
    const thisMonthEvents = events.filter(e => {
        const d = new Date(e.start);
        return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
    });
    document.getElementById('thisMonth').textContent = thisMonthEvents.length;

    // 3. Próximo Evento (dias que faltam)
    // Filtrar apenas eventos futuros
    const futureEvents = events
        .map(e => new Date(e.start))
        .filter(d => d >= now)
        .sort((a, b) => a - b); // Ordenar do mais próximo para o mais distante

    if (futureEvents.length > 0) {
        const nextDate = futureEvents[0];
        const diffTime = Math.abs(nextDate - now);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        let text = diffDays + " dias";
        if (diffDays === 0) text = "Hoje!";
        if (diffDays === 1) text = "Amanhã";

        document.getElementById('nextEventDays').textContent = text;
    } else {
        document.getElementById('nextEventDays').textContent = "-";
    }
}

/**
 * Abre a Modal com detalhes
 */
function showEventModal(event) {
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    const modalLink = document.getElementById('modalLink');
    const bsModal = new bootstrap.Modal(document.getElementById('eventModal'));

    // Título
    modalTitle.textContent = event.title;

    // Data Formatada
    const dateOpts = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    const dateStr = event.start.toLocaleDateString('pt-PT', dateOpts);

    // Construir HTML do corpo
    let html = `
        <div class="mb-3 text-muted"><i class="bi bi-calendar3"></i> ${dateStr}</div>
        <div class="mb-3"><i class="bi bi-geo-alt"></i> <strong>Local:</strong> ${event.extendedProps.location}</div>
        <div class="mb-3"><span class="badge bg-secondary">${event.extendedProps.source}</span></div>
    `;

    // Imagem (se existir)
    if (event.extendedProps.image_url) {
        html += `<img src="${event.extendedProps.image_url}" class="img-fluid rounded mb-3" alt="${event.title}">`;
    }

    modalBody.innerHTML = html;

    // Link do botão
    if (event.extendedProps.url_original) {
        modalLink.href = event.extendedProps.url_original;
        modalLink.style.display = 'inline-block';
    } else {
        modalLink.style.display = 'none';
    }

    bsModal.show();
}