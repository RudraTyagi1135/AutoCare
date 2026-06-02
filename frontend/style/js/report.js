// ==========================================
// AutoCare Report Page JS (FINAL)
// ==========================================

(function () {
  "use strict";

  console.log("📄 Report Page Loaded");

  /* ---------------------------
     HELPERS
  --------------------------- */
  const $ = id => document.getElementById(id);

  function formatDate(date) {
    return new Date(date).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric"
    });
  }

  function formatTime(date) {
    return new Date(date).toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit"
    });
  }

  /* ---------------------------
     DOWNLOAD BUTTON
  --------------------------- */
  function initDownload() {
    const btn = $("downloadReportBtn");
    if (!btn) return;

    btn.addEventListener("click", function () {
      btn.disabled = true;
      btn.innerText = "Preparing...";

      window.location.href = "/download-report";

      setTimeout(() => {
        btn.disabled = false;
        btn.innerText = "Download Report";
      }, 2000);
    });
  }

  /* ---------------------------
     DEMO DATA (Fallback only)
  --------------------------- */
  function demoHistory() {
    return [
      {
        created_at: new Date(),
        prediction: {
          predictions: {
            diabetes: { risk_percent: 65, risk_label: "Moderate" },
            heart: { risk_percent: 42, risk_label: "Moderate" },
            stroke: { risk_percent: 18, risk_label: "Low" }
          }
        }
      },
      {
        created_at: new Date(Date.now() - 86400000),
        prediction: {
          predictions: {
            diabetes: { risk_percent: 25, risk_label: "Low" },
            heart: { risk_percent: 78, risk_label: "High" },
            stroke: { risk_percent: 55, risk_label: "Moderate" }
          }
        }
      }
    ];
  }

  /* ---------------------------
     CREATE HISTORY CARD
  --------------------------- */
  function createCard(record) {
    const card = document.createElement("div");
    card.className = "history-card";

    let html = `
      <div class="card-header">
        <span class="date">${formatDate(record.created_at)}</span>
        <span class="time">${formatTime(record.created_at)}</span>
      </div>

      <div class="card-body">
    `;

    const preds = record?.prediction?.predictions || {};

    Object.keys(preds).forEach(disease => {
      const data = preds[disease];

      html += `
        <div class="disease-row">
          <div class="disease-name">${disease.toUpperCase()}</div>

          <div class="risk-info">
            <span class="risk-percent">${data.risk_percent}%</span>

            <span class="risk-label ${data.risk_label.toLowerCase()}">
              ${data.risk_label}
            </span>
          </div>
        </div>
      `;
    });

    html += `</div>`;

    card.innerHTML = html;

    return card;
  }

  /* ---------------------------
     LOAD HISTORY (SAFE)
  --------------------------- */
  function loadHistory() {
    const grid = document.querySelector(".history-grid");
    const empty = document.querySelector(".empty-state");

    // ✅ CASE 1: Server already rendered records (BEST CASE)
    if (grid && grid.children.length > 0) {
      console.log("✅ Using server-rendered history");
      return;
    }

    // ✅ CASE 2: Use injected JS data (future ready)
    if (window.historyData && window.historyData.length > 0) {
      console.log("📦 Using injected historyData");

      if (empty) empty.style.display = "none";

      window.historyData.forEach(r => {
        grid.appendChild(createCard(r));
      });

      return;
    }

    // ✅ CASE 3: Fallback demo (for testing only)
    console.log("⚠️ No history found → using demo");

    const demo = demoHistory();

    if (!grid) return;

    if (empty) empty.style.display = "none";

    demo.forEach(r => {
      grid.appendChild(createCard(r));
    });
  }

  /* ---------------------------
     INIT
  --------------------------- */
  document.addEventListener("DOMContentLoaded", function () {
    initDownload();
    loadHistory();
  });

})();