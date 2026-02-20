/* FIN.AI — JavaScript partagé */

// ── Toast ────────────────────────────────────────────────────────────────────
function toast(msg, type = 'ok') {
  const el = document.getElementById('toast');
  if (!el) return;
  document.getElementById('toast-msg').textContent = msg;
  el.querySelector('i').style.color = type === 'ok' ? '#6ee09a' : '#f87171';
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2800);
}

// ── Format FCFA ───────────────────────────────────────────────────────────────
function fmt(n) {
  return Math.abs(n).toLocaleString('fr-FR');
}

// ── CSRF helper ───────────────────────────────────────────────────────────────
function getCsrf() {
  const el = document.querySelector('[name=csrfmiddlewaretoken]');
  if (el) return el.value;
  const m = document.cookie.match(/csrftoken=([^;]+)/);
  return m ? m[1] : '';
}

// ── Charts Dashboard ─────────────────────────────────────────────────────────
function initDashCharts(series) {
  const labels  = series.map(s => s.label);
  const incomes = series.map(s => s.income);
  const exps    = series.map(s => s.expense);

  const baseScale = {
    x: { ticks: { color: '#94a3c0', font: { family: 'Plus Jakarta Sans', size: 10 } }, grid: { display: false } },
    y: { display: false }
  };

  // Sparkline héro
  const spark = document.getElementById('c-spark');
  if (spark) {
    new Chart(spark, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          data: incomes.map((v, i) => v - exps[i]),
          borderColor: 'rgba(255,255,255,.7)',
          backgroundColor: 'rgba(255,255,255,.08)',
          fill: true, tension: .5, pointRadius: 0, borderWidth: 2
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { display: false } }
      }
    });
  }

  // Revenus
  const cInc = document.getElementById('c-inc');
  if (cInc) {
    new Chart(cInc, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: incomes,
          backgroundColor: (ctx) => ctx.dataIndex === incomes.length - 1
            ? 'rgba(30,107,72,.9)' : 'rgba(30,107,72,.22)',
          borderRadius: 5, borderSkipped: false
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: baseScale }
    });
  }

  // Dépenses
  const cExp = document.getElementById('c-exp');
  if (cExp) {
    new Chart(cExp, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: exps,
          backgroundColor: (ctx) => ctx.dataIndex === exps.length - 1
            ? 'rgba(192,48,48,.85)' : 'rgba(192,48,48,.2)',
          borderRadius: 5, borderSkipped: false
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: baseScale }
    });
  }
}

// ── Simulateur ────────────────────────────────────────────────────────────────
let SIM_CHART = null;
let SIM_YEARS = 5;

function setHz(years, btn) {
  SIM_YEARS = years;
  document.querySelectorAll('.hz-btn').forEach(b => b.classList.remove('sel'));
  btn.classList.add('sel');
  calcProj();
}

function calcProj() {
  const cap  = parseFloat(document.getElementById('s-capital')?.value) || 0;
  const mon  = parseFloat(document.getElementById('s-monthly')?.value) || 0;
  const rate = parseFloat(document.getElementById('s-rate')?.value || 6) / 100;
  const mths = SIM_YEARS * 12, mRate = rate / 12;

  let wi = cap, co = cap;
  for (let i = 0; i < mths; i++) { wi = wi * (1 + mRate) + mon; co += mon; }

  const valEl  = document.getElementById('proj-val');
  const gainEl = document.getElementById('proj-gain');
  const yEl    = document.getElementById('proj-years');
  if (valEl)  valEl.textContent  = fmt(Math.round(wi));
  if (gainEl) gainEl.textContent = '+' + fmt(Math.round(wi - co)) + ' F de gain vs cash pur';
  if (yEl)    yEl.textContent    = SIM_YEARS;

  // Chart
  const canvas = document.getElementById('c-proj');
  if (!canvas) return;
  const labArr = [], wiArr = [cap], coArr = [cap];
  let wa = cap, ca = cap;
  for (let m = 1; m <= mths; m++) {
    wa = wa * (1 + mRate) + mon; ca += mon;
    if (m % 12 === 0) { labArr.push('An ' + (m / 12)); wiArr.push(Math.round(wa)); coArr.push(Math.round(ca)); }
  }
  if (SIM_CHART) SIM_CHART.destroy();
  SIM_CHART = new Chart(canvas, {
    type: 'line',
    data: {
      labels: labArr,
      datasets: [
        { label: 'Avec investissement', data: wiArr, borderColor: '#1e6b48', backgroundColor: 'rgba(30,107,72,.08)', fill: true, tension: .4, pointBackgroundColor: '#1e6b48', pointRadius: 4 },
        { label: 'Cash pur', data: coArr, borderColor: '#c4b9a8', backgroundColor: 'rgba(196,185,168,.05)', fill: true, tension: .4, pointBackgroundColor: '#c4b9a8', pointRadius: 4, borderDash: [5, 5] }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: true, labels: { color: '#94a3c0', font: { family: 'Plus Jakarta Sans', size: 11 }, boxWidth: 12 } } },
      scales: {
        x: { ticks: { color: '#94a3c0', font: { family: 'Plus Jakarta Sans', size: 10 } }, grid: { color: 'rgba(228,234,244,.6)' } },
        y: { ticks: { color: '#94a3c0', font: { family: 'Plus Jakarta Sans', size: 10 } }, grid: { color: 'rgba(228,234,244,.6)' } }
      }
    }
  });
}

// ── Analyse charts ────────────────────────────────────────────────────────────
function initAnalyseCharts(series, catData) {
  const labels  = series.map(s => s.label);
  const incomes = series.map(s => s.income);
  const exps    = series.map(s => s.expense);

  const rv = document.getElementById('c-rvdep');
  if (rv) {
    new Chart(rv, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          { label: 'Revenus',  data: incomes, backgroundColor: 'rgba(30,107,72,.5)',   borderColor: '#1e6b48', borderWidth: 1, borderRadius: 6 },
          { label: 'Dépenses', data: exps,    backgroundColor: 'rgba(192,48,48,.22)',  borderColor: '#c03030', borderWidth: 1, borderRadius: 6 }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: true, labels: { color: '#94a3c0', font: { family: 'Plus Jakarta Sans', size: 11 }, boxWidth: 12 } } },
        scales: {
          x: { ticks: { color: '#94a3c0', font: { size: 10 } }, grid: { color: 'rgba(228,234,244,.6)' } },
          y: { ticks: { color: '#94a3c0', font: { size: 10 } }, grid: { color: 'rgba(228,234,244,.6)' } }
        }
      }
    });
  }

  const pie = document.getElementById('c-cat');
  if (pie && catData && catData.length) {
    new Chart(pie, {
      type: 'doughnut',
      data: {
        labels: catData.map(c => c.label),
        datasets: [{ data: catData.map(c => c.total), backgroundColor: ['#2d3fa0','#c45c2a','#b87020','#1e6b48','#0891b2','#b83060','#7a5c8a','#c4b9a8'], borderColor: '#fff', borderWidth: 2 }]
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: '60%',
        plugins: { legend: { position: 'right', labels: { color: '#94a3c0', font: { family: 'Plus Jakarta Sans', size: 11 }, boxWidth: 12, padding: 8 } } }
      }
    });
  }
}

// ── SMS Parser (frontend) ─────────────────────────────────────────────────────
async function parseSMS(url, sms) {
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
    body: JSON.stringify({ sms })
  });
  return r.json();
}

// ── Service Worker ────────────────────────────────────────────────────────────
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
      .catch(() => {}); // Silencieux si HTTPS non disponible en dev
  });
}

// ── Push Notifications ────────────────────────────────────────────────────────
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64  = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw     = window.atob(base64);
  return Uint8Array.from([...raw].map(c => c.charCodeAt(0)));
}

function initPushNotifications(vapidPublicKey, subscribeUrl, checkUrl) {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return;

  const icon = document.getElementById('notif-icon');
  const btn  = document.getElementById('notif-btn');

  // Mettre à jour l'icône selon l'état actuel
  if (Notification.permission === 'granted') {
    if (icon) { icon.className = 'fa-solid fa-bell'; icon.style.color = 'var(--forest)'; }
  } else if (Notification.permission === 'denied') {
    if (btn) btn.style.display = 'none';
    return;
  }

  // Vérifier les alertes si déjà abonné
  if (Notification.permission === 'granted') checkPushAlerts(checkUrl);
}

async function requestPushPermission() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    toast('Notifications non supportées par ce navigateur', 'err'); return;
  }
  if (typeof VAPID_PUBLIC_KEY === 'undefined' || !VAPID_PUBLIC_KEY) return;

  const permission = await Notification.requestPermission();
  if (permission !== 'granted') { toast('Notifications refusées', 'err'); return; }

  try {
    const reg  = await navigator.serviceWorker.ready;
    const sub  = await reg.pushManager.subscribe({
      userVisibleOnly:      true,
      applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
    });
    await fetch(PUSH_SUBSCRIBE_URL, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
      body:    JSON.stringify({ subscription: sub.toJSON() }),
    });
    const icon = document.getElementById('notif-icon');
    if (icon) { icon.className = 'fa-solid fa-bell'; icon.style.color = 'var(--forest)'; }
    toast('Notifications activées');
    if (typeof PUSH_CHECK_URL !== 'undefined') checkPushAlerts(PUSH_CHECK_URL);
  } catch (e) {
    toast('Erreur activation notifications', 'err');
  }
}

async function checkPushAlerts(checkUrl) {
  try {
    const r = await fetch(checkUrl);
    const d = await r.json();
    if (d.count > 0) {
      const btn = document.getElementById('notif-btn');
      if (btn && !btn.querySelector('.notif-dot')) {
        const dot = document.createElement('span');
        dot.className = 'notif-dot';
        dot.style.cssText = 'position:absolute;top:4px;right:4px;width:8px;height:8px;border-radius:50%;background:var(--danger);border:2px solid var(--surface);';
        btn.appendChild(dot);
      }
    }
  } catch (e) {}
}

// ── Mise à jour du cookie finai_view lors du redimensionnement ────────────────
(function() {
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      const isMobile = window.innerWidth <= 768;
      const newVal = isMobile ? 'mobile' : 'desktop';
      const current = (document.cookie.match(/finai_view=([^;]+)/) || [])[1];
      document.cookie = 'finai_view=' + newVal + '; max-age=604800; path=/; SameSite=Lax';
      /* Recharge le dashboard si le layout change (portrait ↔ paysage) */
      if (current !== newVal) {
        const p = location.pathname;
        if (p === '/dashboard/' || p === '/') { window.location.reload(); }
      }
    }, 300);
  });
})();
