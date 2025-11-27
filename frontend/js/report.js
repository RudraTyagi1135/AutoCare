// js/report.js — Combined Prediction Viewer + Report Generator

(function () {
  console.log("📄 AutoCare Report System Loaded");

  function by(id) { return document.getElementById(id); }

  const preview = by("reportPreview");
  const genBtn = by("genReport");
  const dlBtn = by("dlReport");

  // === 1️⃣ LOAD STORED PREDICTIONS ===
  const saved = sessionStorage.getItem("autocare_prediction");

  if (!saved) {
    preview.innerHTML = `<div class="preview-line" style="color:#888">
      ⚠ No prediction data found.<br>Return to <strong>Manual Entry</strong> and submit the form.
    </div>`;
    dlBtn.disabled = true;
    return;
  }

  const data = JSON.parse(saved);
  const preds = data.predictions;

  // risk color mapping
  const labelColor = {
    "Low": "#2ecc71",
    "Moderate": "#f4b400",
    "High": "#e74c3c",
    "Very High": "#b60e0e",
    "Severe": "#8B0000"
  };

  // === 2️⃣ BUILD PREVIEW UI ===
  let html = `
    <div class="report-block">
      <h3>🧠 Personal Health Risk Summary</h3>
      <p class="small muted">Based on your clinical and lifestyle inputs.</p>
      <hr>
  `;

  Object.entries(preds).forEach(([disease, r]) => {
    html += `
      <div class="disease-item">
        <h4>${disease.toUpperCase()}</h4>
        <p><strong>Risk Probability:</strong> ${r.risk_percent}%</p>
        <p><strong>Risk Category:</strong> 
          <span style="color:${labelColor[r.risk_label] || '#000'}; font-weight:bold;">
            ${r.risk_label}
          </span>
        </p>
        <p class="small text-muted">Model: ${r.model}</p>
        <hr>
      </div>
    `;
  });

  html += `</div>`;
  preview.innerHTML = html;

  // enable download now that data exists
  dlBtn.disabled = false;


  // === 3️⃣ REPORT GENERATOR ===
  function generateReport() {
    genBtn.disabled = true;
    preview.innerHTML = `<div class="preview-line">📝 Generating report…</div>
      <div class="progress"><div class="bar" style="width:0%"></div></div>`;

    let progress = 0;
    const bar = preview.querySelector('.bar');

    const timer = setInterval(() => {
      progress += Math.random() * 25;
      bar.style.width = Math.min(progress, 95) + "%";

      if (progress >= 90) {
        clearInterval(timer);

        setTimeout(() => {
          const now = new Date().toLocaleString();
          const content = JSON.stringify(data, null, 2);
          const blob = new Blob([content], { type: "application/pdf" });
          const url = URL.createObjectURL(blob);

          dlBtn.href = url;
          dlBtn.download = `AutoCare_Report_${Date.now()}.pdf`;

          preview.innerHTML = `
            <div class="mini-report">
              <strong>Report Ready ✔</strong>
              <div class="small">Generated: ${now}</div>
            </div>
            <a class="download-link" href="${url}" download>⬇ Download PDF</a>
          `;

          genBtn.disabled = false;
        }, 500);
      }
    }, 300);
  }

  // === 4️⃣ HOOK EVENTS ===
  genBtn.addEventListener("click", generateReport);

})();
