// ── Rain Effect ───────────────────────────────────────────
function createRain() {
  const container = document.getElementById('rainContainer');
  for (let i = 0; i < 60; i++) {
    const drop = document.createElement('div');
    drop.className = 'raindrop';
    drop.style.cssText = `
      left: ${Math.random() * 100}%;
      height: ${Math.random() * 60 + 40}px;
      animation-duration: ${Math.random() * 1.5 + 0.8}s;
      animation-delay: ${Math.random() * 3}s;
      opacity: ${Math.random() * 0.3 + 0.05};
    `;
    container.appendChild(drop);
  }
}
createRain();

// ── State ─────────────────────────────────────────────────
let map          = null;
let marker       = null;
let locationData = null;
let suggTimeout  = null;
let activeIndex  = -1;
let suggResults  = [];

// ── DOM refs ──────────────────────────────────────────────
const areaInput   = document.getElementById('areaInput');
const searchBtn   = document.getElementById('searchBtn');
const searchError = document.getElementById('searchError');
const suggestions = document.getElementById('suggestions');
const mapWrap     = document.getElementById('mapWrap');
const terrainWrap = document.getElementById('terrainWrap');
const terrainGrid = document.getElementById('terrainGrid');
const predictWrap = document.getElementById('predictWrap');
const predictBtn  = document.getElementById('predictBtn');
const resultsWrap = document.getElementById('resultsWrap');
const resultsGrid = document.getElementById('resultsGrid');
const summary     = document.getElementById('summary');

// ── Autocomplete ──────────────────────────────────────────
areaInput.addEventListener('input', () => {
  clearTimeout(suggTimeout);
  const q = areaInput.value.trim();

  if (q.length < 2) {
    hideSuggestions();
    return;
  }

  suggestions.classList.remove('hidden');
  suggestions.innerHTML = `
    <div class="sugg-loading">
      <div class="sugg-spinner"></div> Searching locations...
    </div>`;

  suggTimeout = setTimeout(() => fetchSuggestions(q), 350);
});

async function fetchSuggestions(q) {
  try {
    const resp = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}&format=json&limit=6&addressdetails=1&namedetails=1`,
      { headers: { 'User-Agent': 'FloodPredictionApp/1.0' } }
    );
    const data = await resp.json();
    suggResults = data;
    renderSuggestions(data, q);
  } catch {
    hideSuggestions();
  }
}

function renderSuggestions(results, query) {
  activeIndex = -1;

  if (!results.length) {
    suggestions.innerHTML = `<div class="sugg-empty">📭 No locations found for "${query}"</div>`;
    return;
  }

  suggestions.innerHTML = results.map((r, i) => {
    // ✅ FIX: Use the actual result name, not the address city
    const main        = getMainName(r);
    const sub         = getSubName(r);
    const type        = r.type || r.class || 'place';
    const icon        = getLocationIcon(r.type, r.class);
    const highlighted = highlightMatch(main, query);

    return `
      <div class="suggestion-item" data-index="${i}">
        <span class="sugg-icon">${icon}</span>
        <div class="sugg-text">
          <div class="sugg-main">${highlighted}</div>
          ${sub ? `<div class="sugg-sub">${sub}</div>` : ''}
        </div>
        <span class="sugg-type">${type}</span>
      </div>
    `;
  }).join('');

  suggestions.querySelectorAll('.suggestion-item').forEach(el => {
    el.addEventListener('mousedown', (e) => {
      e.preventDefault();
      selectSuggestion(parseInt(el.dataset.index));
    });
  });
}

// ✅ FIX: Always show the actual place name from Nominatim
function getMainName(result) {
  // namedetails.name is the raw OSM name — most accurate
  if (result.namedetails && result.namedetails.name) {
    return result.namedetails.name;
  }
  // Fallback: first part of display_name (before first comma)
  return result.display_name.split(',')[0].trim();
}

// ✅ FIX: Build subtitle from the REST of display_name parts
function getSubName(result) {
  const parts = result.display_name.split(',').map(s => s.trim());

  // Skip the first part (that's the main name), take next 2-3 meaningful parts
  const sub = parts
    .slice(1)
    .filter(p => p && p !== parts[0])   // remove duplicates
    .slice(0, 3)                         // max 3 parts
    .join(', ');

  return sub;
}

function getLocationIcon(type, cls) {
  const iconMap = {
    city          : '🏙️',
    town          : '🏘️',
    village       : '🏡',
    suburb        : '🏢',
    neighbourhood : '🏘️',
    quarter       : '🏙️',
    county        : '🗺️',
    state         : '📍',
    country       : '🌍',
    river         : '🌊',
    lake          : '🏞️',
    mountain      : '⛰️',
    administrative: '🏛️',
    boundary      : '📍',
    station       : '🚉',
    airport       : '✈️',
    hospital      : '🏥',
    school        : '🏫',
    university    : '🎓',
    park          : '🌳',
    beach         : '🏖️',
  };
  return iconMap[type] || iconMap[cls] || '📍';
}

function highlightMatch(text, query) {
  const escaped = query.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
  const regex   = new RegExp(`(${escaped})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
}

function selectSuggestion(idx) {
  const r = suggResults[idx];
  if (!r) return;

  // ✅ Put the actual place name in the input
  areaInput.value = getMainName(r);
  hideSuggestions();

  // Pass the full display_name to backend for accurate geocoding
  doSearch(r.display_name);
}

function hideSuggestions() {
  suggestions.classList.add('hidden');
  suggestions.innerHTML = '';
  activeIndex = -1;
}

// Keyboard navigation
areaInput.addEventListener('keydown', (e) => {
  const items = suggestions.querySelectorAll('.suggestion-item');

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    activeIndex = Math.min(activeIndex + 1, items.length - 1);
    updateActiveItem(items);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    activeIndex = Math.max(activeIndex - 1, -1);
    updateActiveItem(items);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (activeIndex >= 0 && items[activeIndex]) {
      selectSuggestion(activeIndex);
    } else {
      doSearch();
    }
  } else if (e.key === 'Escape') {
    hideSuggestions();
  }
});

function updateActiveItem(items) {
  items.forEach((el, i) => el.classList.toggle('active', i === activeIndex));
}

document.addEventListener('click', (e) => {
  if (!e.target.closest('.search-wrap')) hideSuggestions();
});

// ── Search ────────────────────────────────────────────────
searchBtn.addEventListener('click', () => doSearch());

async function doSearch(overrideName) {
  const area = overrideName || areaInput.value.trim();
  if (!area) return showError('Please enter an area name.');

  hideSuggestions();
  setSearchLoading(true);
  hideError();
  hideResults();

  try {
    const resp = await fetch('/search', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ area })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Search failed.');

    locationData = data;
    showMap(data);
    showTerrain(data.terrain);
    predictWrap.classList.remove('hidden');

  } catch (err) {
    showError(err.message);
  } finally {
    setSearchLoading(false);
  }
}

// ── Map ───────────────────────────────────────────────────
function showMap(data) {
  mapWrap.classList.remove('hidden');

  if (!map) {
    map = L.map('map', { zoomControl: true }).setView([data.lat, data.lon], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap'
    }).addTo(map);
  } else {
    map.setView([data.lat, data.lon], 12);
    if (marker) map.removeLayer(marker);
  }

  const customIcon = L.divIcon({
    html: `<div style="
      background:linear-gradient(135deg,#1565c0,#0288d1);
      width:36px;height:36px;border-radius:50% 50% 50% 0;
      transform:rotate(-45deg);border:3px solid #fff;
      box-shadow:0 4px 16px rgba(2,136,209,0.6);
      display:flex;align-items:center;justify-content:center;">
      <span style="transform:rotate(45deg);font-size:14px;">📍</span>
    </div>`,
    iconSize   : [36, 36],
    iconAnchor : [18, 36],
    className  : ''
  });

  marker = L.marker([data.lat, data.lon], { icon: customIcon })
    .addTo(map)
    .bindPopup(`<b style="color:#1565c0">${data.display_name}</b>`)
    .openPopup();

  document.getElementById('coordBadge').textContent =
    `${data.lat.toFixed(4)}°N, ${data.lon.toFixed(4)}°E`;

  document.getElementById('locationInfo').innerHTML =
    `📍 <strong style="color:#90caf9">${data.display_name}</strong>
     &nbsp;·&nbsp; Elevation: <strong style="color:#e3f2fd">${data.terrain.elevation} m</strong>`;
}

// ── Terrain ───────────────────────────────────────────────
function showTerrain(terrain) {
  terrainWrap.classList.remove('hidden');

  const items = [
    { key: 'Slope',     label: 'Slope (°)',    icon: '⛰️' },
    { key: 'Curvature', label: 'Curvature',    icon: '〰️' },
    { key: 'Aspect',    label: 'Aspect (°)',   icon: '🧭' },
    { key: 'TWI',       label: 'TWI',          icon: '💧' },
    { key: 'FA',        label: 'Flow Accum.',  icon: '🌊' },
    { key: 'Drainage',  label: 'Drainage (m)', icon: '🏔️' },
    { key: 'elevation', label: 'Elevation (m)',icon: '📏' },
  ];

  terrainGrid.innerHTML = items.map(item => `
    <div class="terrain-item">
      <div class="t-label">${item.icon} ${item.label}</div>
      <div class="t-value">${terrain[item.key] ?? '—'}</div>
    </div>
  `).join('');
}

document.getElementById('terrainToggle').addEventListener('click', () => {
  const body = document.getElementById('terrainBody');
  const icon = document.querySelector('.toggle-icon');
  const open = body.style.display !== 'none';
  body.style.display   = open ? 'none' : 'block';
  icon.style.transform = open ? 'rotate(-90deg)' : 'rotate(0deg)';
  icon.textContent     = open ? '▶' : '▼';
});

// ── Predict ───────────────────────────────────────────────
predictBtn.addEventListener('click', doPredict);

async function doPredict() {
  if (!locationData) return;

  predictBtn.disabled = true;
  document.querySelector('.predict-text').textContent = 'Analyzing...';
  document.querySelector('.predict-icon').textContent = '⏳';
  hideResults();

  try {
    const resp = await fetch('/predict', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({
        terrain : locationData.terrain,
        forecast: locationData.forecast
      })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Prediction failed.');
    showResults(data.predictions);
  } catch (err) {
    showError(err.message);
  } finally {
    predictBtn.disabled = false;
    document.querySelector('.predict-text').textContent = 'Predict Flood Risk for Next 3 Days';
    document.querySelector('.predict-icon').textContent = '🌧️';
  }
}

// ── Results ───────────────────────────────────────────────
function getRiskConfig(riskLevel) {
  const configs = {
    'Low'      : { icon:'🟢', color:'#66bb6a', cssClass:'risk-low',      barBg:'linear-gradient(90deg,#43a047,#66bb6a)' },
    'Moderate' : { icon:'🟡', color:'#ffca28', cssClass:'risk-moderate', barBg:'linear-gradient(90deg,#f9a825,#ffca28)' },
    'High'     : { icon:'🟠', color:'#ff7043', cssClass:'risk-high',     barBg:'linear-gradient(90deg,#e64a19,#ff7043)' },
    'Very High': { icon:'🔴', color:'#ef5350', cssClass:'risk-veryhigh', barBg:'linear-gradient(90deg,#b71c1c,#ef5350)' },
  };
  return configs[riskLevel] || configs['Low'];
}

function showResults(predictions) {
  resultsWrap.classList.remove('hidden');
  document.getElementById('resultsLocation').textContent = locationData?.display_name || '';

  resultsGrid.innerHTML = predictions.map(p => {
    const cfg = getRiskConfig(p.risk_level);
    return `
      <div class="day-card ${cfg.cssClass}">
        <span class="day-risk-icon"
              style="filter:drop-shadow(0 0 14px ${cfg.color}88)">${cfg.icon}</span>
        <div class="day-date">${formatDate(p.date)}</div>
        <div class="day-risk-label" style="color:${cfg.color}">${p.risk_level} Risk</div>
        <div class="day-prob" style="color:${cfg.color}">${p.probability}%</div>
        <div class="day-prob-label">Flood Probability</div>
        <div class="prob-bar-wrap">
          <div class="prob-bar"
               style="width:0%;background:${cfg.barBg}"
               data-width="${p.probability}"></div>
        </div>
        <div class="day-details">
          <div class="detail-row">
            <span class="d-icon">🌧️</span><span>Rainfall</span>
            <span class="d-val">${p.rainfall_mm} mm</span>
          </div>
          <div class="detail-row">
            <span class="d-icon">⏱️</span><span>Rain hours</span>
            <span class="d-val">${p.hours_rain} hrs</span>
          </div>
          <div class="detail-row">
            <span class="d-icon">💧</span><span>Peak rate</span>
            <span class="d-val">${p.max_hourly_mm} mm/hr</span>
          </div>
        </div>
        <div class="flood-status ${p.flood ? 'danger' : 'safe'}">
          ${p.flood ? '⚠️ Flood Likely' : '✅ Safe'}
        </div>
      </div>
    `;
  }).join('');

  requestAnimationFrame(() => {
    setTimeout(() => {
      document.querySelectorAll('.prob-bar').forEach(bar => {
        bar.style.width = bar.dataset.width + '%';
      });
    }, 100);
  });

  const floodDays = predictions.filter(p => p.flood).length;
  const maxRisk   = predictions.reduce((a, b) => a.probability > b.probability ? a : b);
  const totalRain = predictions.reduce((s, p) => s + p.rainfall_mm, 0);

  let summaryIcon, summaryText;
  if (floodDays === 0) {
    summaryIcon = '✅';
    summaryText = `<strong>No flood risk</strong> detected for the next 3 days.
      Total expected rainfall: <strong>${totalRain.toFixed(1)} mm</strong>.
      Conditions appear safe — no immediate action required.`;
  } else if (floodDays === 1) {
    summaryIcon = '⚠️';
    summaryText = `<strong>Flood risk on 1 day</strong> in the next 3 days.
      Peak probability: <strong>${maxRisk.probability}%</strong>
      on <strong>${formatDate(maxRisk.date)}</strong>.
      Total rainfall: <strong>${totalRain.toFixed(1)} mm</strong>. Stay alert.`;
  } else {
    summaryIcon = '🚨';
    summaryText = `<strong>Flood risk on ${floodDays} days</strong> in the next 3 days.
      Peak probability: <strong>${maxRisk.probability}%</strong>
      on <strong>${formatDate(maxRisk.date)}</strong>.
      Total rainfall: <strong>${totalRain.toFixed(1)} mm</strong>.
      Take precautions immediately.`;
  }

  summary.innerHTML = `<span class="summary-icon">${summaryIcon}</span>${summaryText}`;
}

// ── Helpers ───────────────────────────────────────────────
function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-IN', {
    weekday: 'short', month: 'short', day: 'numeric'
  });
}

function showError(msg) {
  searchError.textContent = '⚠ ' + msg;
  searchError.classList.remove('hidden');
}

function hideError()   { searchError.classList.add('hidden'); }
function hideResults() { resultsWrap.classList.add('hidden'); }

function setSearchLoading(loading) {
  searchBtn.disabled = loading;
  document.querySelector('.btn-text').textContent = loading ? 'Searching...' : 'Search';
}
