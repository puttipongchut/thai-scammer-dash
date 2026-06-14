const SEV_COLORS = { critical: '#A6362C', high: '#C1672E', medium: '#B6862C', low: '#4B7755' };

const map = L.map('map').setView([13.0, 101.5], 6);
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap © CARTO',
    subdomains: 'abcd', maxZoom: 18,
}).addTo(map);

const fmt = n => new Intl.NumberFormat('en-TH').format(n);
let markers = [];

function clearMarkers() {
    markers.forEach(m => map.removeLayer(m));
    markers = [];
}

function addMarker(props) {
    const color = SEV_COLORS[props.severity] || '#64748b';
    const icon = L.divIcon({
        html: `<div style="width:12px;height:12px;background:${color};border-radius:50%;box-shadow:0 0 8px ${color}88"></div>`,
        className: '', iconSize: [12, 12], iconAnchor: [6, 6],
    });
    const marker = L.marker([props.lat, props.lng], { icon }).addTo(map);
    marker.bindPopup(`
    <div class="popup-title">${props.title}</div>
    <div class="popup-summary">${props.summary || ''}</div>
  `);
    markers.push(marker);
}

function renderStats(stats) {
    document.getElementById('kpi-rows').innerHTML = `
    <div class="kpi-row"><div class="kpi-label">Incidents</div><div class="kpi-value accent">${stats.totalIncidents}</div></div>
    <div class="kpi-row"><div class="kpi-label">Critical</div><div class="kpi-value warn">${stats.criticalAlerts}</div></div>
    <div class="kpi-row"><div class="kpi-label">Victims</div><div class="kpi-value">${fmt(stats.totalVictims)}</div></div>
    <div class="kpi-row"><div class="kpi-label">Provinces</div><div class="kpi-value">${stats.activeProvinces}</div></div>
  `;
    document.getElementById('last-updated').textContent =
        'Updated ' + new Date(stats.lastUpdated).toLocaleTimeString('en-TH');

    document.getElementById('cat-list').innerHTML = Object.entries(stats.byCategory).map(([key, cat]) => `
    <div class="cat-row">
      <div class="cat-tab" style="background:${cat.color}"></div>
      <div class="cat-name">${cat.label}</div>
      <div class="cat-count">${cat.count}</div>
    </div>
  `).join('');
}

function renderFeed(incidents) {
    document.getElementById('incident-feed').innerHTML = incidents.map(inc => {
        const ref = 'REF-' + (inc.date || '').replace(/-/g, '') + '-' + String(inc.id).padStart(3, '0');
        return `
    <div class="feed-item sev-${inc.severity}" onclick="focusIncident(${inc.lat}, ${inc.lng})">
      <div class="feed-ref">${ref} · ${inc.severity.toUpperCase()}</div>
      <div class="feed-title">${inc.title}</div>
      <div class="feed-meta"><span>${inc.province}</span><span>${inc.source}</span></div>
    </div>`;
    }).join('');
}

function focusIncident(lat, lng) {
    map.flyTo([lat, lng], 10, { duration: 1 });
}

async function loadDashboard() {
    const [geo, stats, recent] = await Promise.all([
        fetch('/api/incidents').then(r => r.json()),
        fetch('/api/stats').then(r => r.json()),
        fetch('/api/recent').then(r => r.json()),
    ]);

    clearMarkers();
    geo.features.forEach(f => addMarker(f.properties));

    renderStats(stats);
    renderFeed(recent);
}

loadDashboard();
setInterval(loadDashboard, 5 * 60 * 1000);