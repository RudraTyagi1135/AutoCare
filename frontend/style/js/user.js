// static/js/user.js
// Final polished dashboard JS: sparklines, count-up, risk bars, SHAP bars, nav fix, demo fallback.
(function () {
  'use strict';

  /* ---------------------------
     Helpers
  --------------------------- */
  const $ = id => document.getElementById(id);
  const qsAll = sel => Array.from(document.querySelectorAll(sel));
  const clamp = (v, a = 0, b = 100) => Math.max(a, Math.min(b, v));
  const easeOutCubic = t => 1 - Math.pow(1 - t, 3);

  function safeChartDestroy(canvas) {
    try {
      if (canvas && canvas._chart) {
        canvas._chart.destroy();
        canvas._chart = null;
      }
    } catch (e) {
      console.warn('chart destroy failed', e);
    }
  }

  /* ---------------------------
     Demo data (safe fallback)
     Used when window.predictionData is null
  --------------------------- */
  function demoPredictionData() {
    function randHistory() {
      let v = Math.random() * 0.5 + 0.25;
      return new Array(8).fill(0).map(() => {
        v = clamp(v + (Math.random() - 0.45) * 0.08, 0, 1);
        return Number(v.toFixed(3));
      });
    }
    function randShap() {
      const features = ['age','bmi','bp','chol','smoking','glucose','activity'];
      return features.slice(0, 5).map(f => ({
        feature: f,
        impact: Number((Math.random() * 0.28 * (Math.random() > 0.6 ? 1 : -1)).toFixed(3))
      }));
    }
    return {
      predictions: {
        diabetes: { risk_percent: Math.round((0.2 + Math.random()*0.6) * 100), history: randHistory(), explainability: { top_contributors: randShap() } },
        heart:    { risk_percent: Math.round((0.1 + Math.random()*0.7) * 100), history: randHistory(), explainability: { top_contributors: randShap() } },
        stroke:   { risk_percent: Math.round((0.05 + Math.random()*0.6) * 100), history: randHistory(), explainability: { top_contributors: randShap() } }
      }
    };
  }

  /* ---------------------------
     Nav handling (fix routes + active link)
  --------------------------- */
  function initNav() {
    const links = qsAll('.topnav .nav-link');
    const path = window.location.pathname.replace(/\/+$/, '') || '/';

    // client-side active link highlight (fallback to server-side)
    links.forEach(link => {
      try {
        const href = link.getAttribute('href') || '';
        // normalize
        const normalized = (new URL(href, window.location.origin)).pathname.replace(/\/+$/, '') || '/';
        if (normalized === path) link.classList.add('active');
        else link.classList.remove('active');
      } catch (e) {
        // ignore relative/hash urls
      }

      // only prevent navigation for href="#" links (common placeholders)
      link.addEventListener('click', (ev) => {
        const href = link.getAttribute('href') || '';
        if (href === '#') {
          ev.preventDefault();
        }
      });
    });
  }

  /* ---------------------------
     Sparkline (small trend)
  --------------------------- */
  function renderSparkline(canvasId, values) {
    const canvas = $(canvasId);
    if (!canvas || !Array.isArray(values)) return;
    safeChartDestroy(canvas);
    const ctx = canvas.getContext('2d');
    try {
      canvas._chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: values.map((_, i) => i+1),
          datasets: [{
            data: values.map(v => v * 100),
            fill: true,
            tension: 0.35,
            borderWidth: 1.5,
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37,99,235,0.08)',
            pointRadius: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          elements: { line: { capStyle: 'round' } },
          scales: { x: { display: false }, y: { display: false } },
          plugins: { legend: { display: false }, tooltip: { enabled: false } }
        }
      });
    } catch (e) {
      console.error('sparkline error', e);
    }
  }

  /* ---------------------------
     SHAP horizontal bars
  --------------------------- */
  function createShapBars(canvasId, contributors) {
    const canvas = $(canvasId);
    if (!canvas) return;
    safeChartDestroy(canvas);
    const ctx = canvas.getContext('2d');

    if (!Array.isArray(contributors) || contributors.length === 0) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      return;
    }

    const labels = contributors.map(c => c.feature || c.name || 'feature');
    const values = contributors.map(c => Math.abs(c.impact || 0));
    const maxVal = Math.max(...values, 0.1);
    const maxScale = Math.ceil(maxVal * 1.4 * 10) / 10;
    const colors = contributors.map(c => (c.impact >= 0 ? '#ef4444' : '#0b5ecf'));

    try {
      canvas._chart = new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets: [{ data: values, backgroundColor: colors, borderRadius: 6, barThickness: 14 }] },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: { label: ctx => ((ctx.raw * 100).toFixed(1) + '% influence') }
            }
          },
          scales: {
            x: { beginAtZero: true, max: maxScale, grid: { color: '#eef6ff' }, ticks: { callback: v => (v * 100).toFixed(0) + '%' } },
            y: { grid: { display: false }, ticks: { color: '#0b2338', font: { size: 13 } } }
          }
        }
      });
    } catch (e) {
      console.error('shap chart error', e);
    }
  }

  /* ---------------------------
     Risk bar animation + count
  --------------------------- */
  function animateCount(el, target) {
    if (!el) return;
    const start = parseInt(el.textContent, 10) || 0;
    const duration = Math.min(900, Math.max(450, target * 8));
    const t0 = performance.now();
    function step(t) {
      const p = Math.min(1, (t - t0) / duration);
      const v = Math.round(start + (target - start) * easeOutCubic(p));
      el.textContent = v + '%';
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function animateRiskBar(trackId, percent) {
    const fill = $(trackId);
    if (!fill) return;
    // remove glow classes
    fill.classList.remove('glow-high', 'glow-mid');
    // set width
    setTimeout(() => {
      fill.style.width = clamp(percent, 0, 100) + '%';
      if (percent >= 70) fill.classList.add('glow-high');
      else if (percent >= 40) fill.classList.add('glow-mid');
    }, 90);
  }

  function riskClass(percent) {
    if (percent >= 70) return 'risk-high';
    if (percent >= 40) return 'risk-mid';
    return 'risk-low';
  }

  /* ---------------------------
     Populate reasons list
  --------------------------- */
  function populateReasons(listEl, contributors) {
    if (!listEl) return;
    listEl.innerHTML = '';
    if (!Array.isArray(contributors) || contributors.length === 0) {
      const li = document.createElement('li');
      li.textContent = 'No prominent factors available';
      listEl.appendChild(li);
      return;
    }
    contributors.slice(0, 5).forEach((c, i) => {
      const li = document.createElement('li');
      li.innerHTML = `<strong>${i+1}. ${c.feature || c.name || 'feature'}</strong>
                      <div class="reason-sub">impact ${Number(c.impact || 0).toFixed(3)}</div>`;
      listEl.appendChild(li);
    });
  }

  /* ---------------------------
     Panel updater
  --------------------------- */
  function updatePanel(cfg, sourceData) {
    const data = sourceData?.predictions?.[cfg.key];
    if (!data) return;

    // percent is stored as integer (0..100) in our data model
    const percent = Math.round(data.risk_percent ?? (data.probability ? Math.round(data.probability * 100) : 0));

    // badge
    const badge = $(cfg.riskId);
    if (badge) {
      badge.className = 'risk-badge ' + riskClass(percent);
      animateCount(badge, percent);
    }

    // track
    animateRiskBar(cfg.trackId, percent);

    // sparkline (history || trend)
    const hist = data.history || data.trend || [];
    renderSparkline(cfg.sparkId, hist.length ? hist : Array(8).fill(percent / 100));

    // reasons
    const contributors = data.explainability?.top_contributors || data.top_features || [];
    populateReasons($(cfg.reasonId), contributors);

    // shap
    createShapBars(cfg.shapId, contributors.slice(0, 6));
  }

  /* ---------------------------
     Main initialization
  --------------------------- */
  document.addEventListener('DOMContentLoaded', function () {
    initNav();

    // If Chart is not loaded, warn and exit gracefully (no crash).
    if (typeof Chart === 'undefined') {
      console.warn('Chart.js is not loaded — charts will not render.');
    }

    const panels = [
      { key: 'diabetes', riskId: 'risk-diabetes', trackId: 'risk-diabetes-track', sparkId: 'spark-diabetes', reasonId: 'reasons-diabetes', shapId: 'shap-diabetes-canvas' },
      { key: 'heart',    riskId: 'risk-heart',    trackId: 'risk-heart-track',    sparkId: 'spark-heart',    reasonId: 'reasons-heart',    shapId: 'shap-heart-canvas' },
      { key: 'stroke',   riskId: 'risk-stroke',   trackId: 'risk-stroke-track',   sparkId: 'spark-stroke',   reasonId: 'reasons-stroke',   shapId: 'shap-stroke-canvas' }
    ];

    // Use server-provided predictionData if present; otherwise fallback to demo
    const source = window.predictionData || demoPredictionData();

    // Staggered rendering for nicer UX
    panels.forEach((p, i) => setTimeout(() => updatePanel(p, source), i * 220));
  });

  // expose for debugging if needed
  window._autocare = { demoPredictionData };

})();
