// js/report.js
// Reports page: generate simulated PDF, enable download link, preview and progress

(function(){
  function by(id){ return document.getElementById(id); }
  function createBlobPdf(content){
    // simulate a PDF with a text blob but use application/pdf type
    return new Blob([content], { type: 'application/pdf' });
  }

  function generateReport(){
    const status = by('reportPreview');
    const genBtn = by('genReport');
    const dlBtn = by('dlReport');
    if(genBtn) genBtn.disabled = true;
    if(status) status.innerHTML = '<div class="preview-line">Generating report…</div><div class="progress"><div class="bar" style="width:0%"></div></div>';
    // animate progress and then create blob
    let pct = 0;
    const bar = status && status.querySelector('.bar');
    const t = setInterval(()=>{
      pct += Math.floor(Math.random()*22)+8;
      if(bar) bar.style.width = Math.min(pct,95) + '%';
      if(pct >= 92){
        clearInterval(t);
        setTimeout(()=>{
          const now = new Date().toLocaleString();
          const content = `AutoCare Report\nGenerated: ${now}\n\n(Simulated PDF content for preview)`;
          const blob = createBlobPdf(content);
          const url = URL.createObjectURL(blob);
          if(dlBtn){
            dlBtn.href = url;
            dlBtn.download = `autocare-report-${Date.now()}.pdf`;
            dlBtn.disabled = false;
          }
          if(status) status.innerHTML = `<div class="mini-report"><div class="meta">Report generated</div><div class="when">${now}</div></div><div style="margin-top:8px"><a class="download-link" href="${url}" download>Download PDF</a></div>`;
          if(genBtn) genBtn.disabled = false;
        }, 400);
      }
    }, 220);
  }

  function downloadReport(){
    // when download button is clicked, the anchor's href will trigger download.
    const status = by('reportPreview');
    if(status) status.insertAdjacentHTML('beforeend','<div class="preview-line">Download started.</div>');
  }

  function initReports(){
    const gen = by('genReport');
    const dl = by('dlReport');
    if(gen) gen.addEventListener('click', generateReport);
    if(dl) dl.addEventListener('click', downloadReport);
  }

  document.addEventListener('DOMContentLoaded', initReports);
  window.initReports = initReports;
  window.generateReport = generateReport;
  window.downloadReport = downloadReport;
})();
