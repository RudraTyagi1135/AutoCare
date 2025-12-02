// dataupload.js — drag & drop, browse, CSV preview and a simple "analysis" simulation
(function () {
  'use strict';

  const dz = document.getElementById('largeDropzone');
  const fileInput = document.getElementById('fileInput');
  const browseBtn = document.getElementById('browseBtn');
  const uploadPreview = document.getElementById('upload-preview');
  const analysisPreview = document.getElementById('analysis-preview');
  const analysisSummary = document.getElementById('analysis-summary');
  const analysisBody = document.getElementById('analysis-body');
  const resultBtn = document.getElementById('resultBtn');
  const backBtn = document.getElementById('backBtn');

  let lastFile = null;
  const MAX_MB = 20;

  // Helpers
  function showMessage(html) {
    if (uploadPreview) uploadPreview.innerHTML = html;
  }

  function setDisabled(el, state) {
    if (!el) return;
    el.disabled = state;
    el.classList.toggle('disabled', state);
  }

  function escapeHtml(s) {
    if (!s && s !== 0) return '';
    return String(s).replace(/[&<>]/g, c => ( { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c] ));
  }

  // Simple CSV parser (naive) and preview generator
  function parseCsvLine(line) {
    const out = [];
    let cur = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (inQuotes && line[i + 1] === '"') { cur += '"'; i++; continue; }
        inQuotes = !inQuotes;
        continue;
      }
      if (ch === ',' && !inQuotes) {
        out.push(cur);
        cur = '';
        continue;
      }
      cur += ch;
    }
    out.push(cur);
    return out;
  }

  function csvPreviewTable(text, maxRows) {
    const lines = text.replace(/\r/g, '').split('\n').filter(Boolean);
    if (lines.length === 0) return '<div class="small">Empty CSV</div>';
    const rows = [];
    for (let i = 0; i < Math.min(lines.length, maxRows); i++) {
      rows.push(parseCsvLine(lines[i]));
    }
    const header = parseCsvLine(lines[0]);
    let html = '<table><thead><tr>' + header.slice(0, 8).map(h => `<th>${escapeHtml(h)}</th>`).join('') + '</tr></thead><tbody>';
    for (let r = 1; r < rows.length; r++) {
      html += '<tr>' + rows[r].slice(0, 8).map(c => `<td>${escapeHtml(c)}</td>`).join('') + '</tr>';
    }
    html += '</tbody></table>';
    return html;
  }

  // Handle a selected file
  function handleFile(file) {
    lastFile = file;
    if (!file) return;

    const mb = file.size / (1024 * 1024);
    if (mb > MAX_MB) {
      showMessage(`<div class="small" style="color:#ffb4b4">File too large (${mb.toFixed(1)} MB). Max ${MAX_MB} MB.</div>`);
      setDisabled(resultBtn, true);
      return;
    }

    showMessage(`<div style="font-weight:700">Selected file:</div>
      <div class="small">${escapeHtml(file.name)} · ${(file.size / 1024).toFixed(0)} KB · ${escapeHtml(file.type || 'n/a')}</div>`);

    // CSV: read and show small preview
    if (file.name.toLowerCase().endsWith('.csv')) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const text = e.target.result;
        const tableHtml = csvPreviewTable(text, 5);
        uploadPreview.innerHTML = `<div style="font-weight:700;margin-bottom:6px">Preview (first rows)</div>` + tableHtml;
        setDisabled(resultBtn, false);
      };
      reader.onerror = function () {
        showMessage(`<div class="small">Unable to read CSV file.</div>`);
        setDisabled(resultBtn, true);
      };
      reader.readAsText(file);

    } else if (/\.xls|\.xlsx$/i.test(file.name)) {
      uploadPreview.innerHTML = `<div style="font-weight:700">Excel file detected</div><div class="small">Preview not available in this lightweight build — results will still be generated from the file on the server.</div>`;
      setDisabled(resultBtn, false);

    } else if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
      uploadPreview.innerHTML = `<div style="font-weight:700">PDF uploaded</div><div class="small">Preview not available here. PDF will be parsed server-side.</div>`;
      setDisabled(resultBtn, false);

    } else {
      uploadPreview.innerHTML = `<div class="small">Unsupported file type — allowed: CSV, XLSX, XLS, PDF</div>`;
      setDisabled(resultBtn, true);
    }
  }

  // Drag & drop wiring
  if (dz) {
    ['dragenter', 'dragover'].forEach(ev => dz.addEventListener(ev, e => {
      e.preventDefault(); e.stopPropagation();
      dz.classList.add('dragover');
    }));

    ['dragleave', 'drop'].forEach(ev => dz.addEventListener(ev, e => {
      e.preventDefault(); e.stopPropagation();
      dz.classList.remove('dragover');
    }));

    dz.addEventListener('drop', function (e) {
      const f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
      if (f) handleFile(f);
    });

    dz.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        if (fileInput) fileInput.click();
      }
    });
  }

  // Browse button wiring
  if (browseBtn) browseBtn.addEventListener('click', () => fileInput && fileInput.click());
  if (fileInput) fileInput.addEventListener('change', (e) => {
    const f = e.target.files && e.target.files[0];
    if (f) handleFile(f);
  });

  // Result button: simulate analysis (replace with server call in production)
  if (resultBtn) {
    resultBtn.addEventListener('click', function () {
      if (!lastFile) return;

      setDisabled(resultBtn, true);
      showMessage(`<div style="font-weight:700">Analyzing...</div><div class="small">Simulating analysis — results will be generated server-side in production.</div>`);

      setTimeout(function () {
        setDisabled(resultBtn, false);
        if (analysisPreview) analysisPreview.style.display = '';
        if (analysisSummary) analysisSummary.textContent = `File: ${lastFile.name}`;

        const seed = (String(lastFile.name) + lastFile.size).split('').reduce((s, c) => s + c.charCodeAt(0), 0);
        const diabetes = (seed % 60) + 10; // 10-69
        const heart = (seed % 50) + 5;
        const stroke = (seed % 40) + 3;

        if (analysisBody) {
          analysisBody.innerHTML = `
            <div style="display:flex;gap:12px;flex-wrap:wrap">
              <div style="min-width:160px">
                <div style="font-weight:700">Diabetes</div>
                <div class="small muted">Risk: <strong>${diabetes}%</strong></div>
                <div class="small">Top contributors:</div>
                <ol class="small muted"><li>Glucose</li><li>BMI</li><li>Age</li><li>HbA1c</li><li>Family history</li></ol>
              </div>
              <div style="min-width:160px">
                <div style="font-weight:700">Heart Disease</div>
                <div class="small muted">Risk: <strong>${heart}%</strong></div>
                <div class="small">Top contributors:</div>
                <ol class="small muted"><li>BP systolic</li><li>Cholesterol</li><li>Age</li><li>Smoking</li><li>ECG flags</li></ol>
              </div>
              <div style="min-width:160px">
                <div style="font-weight:700">Stroke</div>
                <div class="small muted">Risk: <strong>${stroke}%</strong></div>
                <div class="small">Top contributors:</div>
                <ol class="small muted"><li>BP trends</li><li>AF flag</li><li>Smoking</li><li>Diabetes</li><li>Age</li></ol>
              </div>
            </div>
          `;
        }

        uploadPreview.innerHTML = `<div style="font-weight:700">Analysis complete</div><div class="small">This is a simulated result preview. Replace with server response handling as needed.</div>`;
      }, 900);
    });
  }

  if (backBtn) {
    backBtn.addEventListener('click', () => {
      location.href = 'user.html';
    });
  }

})();
