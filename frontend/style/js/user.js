// js/user.js
(function(){
  // ----------------------
  // helpers
  // ----------------------
  function by(id){ return document.getElementById(id); }
  function qa(sel, root=document){ return Array.from((root||document).querySelectorAll(sel)); }
  function randSeries(n, min, max){ return Array.from({length:n}, () => Math.floor(Math.random()*(max-min)+min)); }

  // ----------------------
  // Charts (core logic)
  // ----------------------
  let diabetesChart=null, heartChart=null, strokeChart=null;

  function hexToRgba(hex, a){
    if(!hex) return `rgba(11,94,207,${a})`;
    hex = hex.replace('#','').trim();
    if(hex.length===3) hex = hex.split('').map(c=>c+c).join('');
    const i = parseInt(hex,16);
    const r = (i>>16)&255, g=(i>>8)&255, b=i&255;
    return `rgba(${r},${g},${b},${a})`;
  }

  function computeRiskFromData(arr){
    if(!arr || !arr.length) return 0;
    const avg = arr.reduce((s,v)=>s+v,0)/arr.length;
    return Math.round(avg);
  }

  function riskClass(p){
    if(p>=70) return 'risk-high';
    if(p>=40) return 'risk-mid';
    return 'risk-low';
  }

  function syncPanelWithChart(chart, riskElId, reasonsElId, features){
    try{
      const data = (chart && chart.data && chart.data.datasets && chart.data.datasets[0].data) || [];
      const risk = computeRiskFromData(data);
      const rEl = by(riskElId);
      if(rEl){ rEl.textContent = risk + '%'; rEl.className = 'risk-badge ' + riskClass(risk); }

      const reasonsEl = by(reasonsElId);
      if(!reasonsEl) return;
      const f = (features && features.length) ? features.slice() : ['Elevated lab value','Abnormal vitals','Relevant med history','Imaging flag','Age/comorbidity'];
      const last = data[data.length-1]||0, mid = data[Math.floor(data.length/2)]||0;
      const variance = Math.round(Math.abs(last-mid))||5;
      const scored = f.map((s,i)=>({f:s, score: Math.round((Math.random()*20)+(last/3)-(i*2)+(variance/3))})).sort((a,b)=>b.score-a.score);
      let html='';
      for(let i=0;i<Math.min(5,scored.length);i++){
        const item = scored[i];
        const color = i===0 ? (getComputedStyle(document.body).getPropertyValue('--accent')||'#0b5ecf').trim() : (i===1 ? '#d9534f' : (i===2 ? '#6f42c1' : '#b0b0b0'));
        html += `<li><span class="dot" style="background:${color}"></span><div class="reason-text">${item.f}<span class="reason-sub">relative importance ${item.score}</span></div></li>`;
      }
      reasonsEl.innerHTML = html;
    }catch(e){
      console.warn('syncPanelWithChart error', e);
    }
  }

  function createGradient(ctx, area, color){
    const g = ctx.createLinearGradient(0,0,0,area.bottom);
    g.addColorStop(0, hexToRgba(color,0.20));
    g.addColorStop(1, hexToRgba(color,0.02));
    return g;
  }

  function createOrUpdateLine(canvasId, opts){
    const canvas = by(canvasId);
    if(!canvas) return null;
    if(typeof Chart === 'undefined'){ setTimeout(()=>createOrUpdateLine(canvasId,opts),40); return null; }
    const ctx = canvas.getContext('2d');
    if(canvas._chart) try{ canvas._chart.destroy(); }catch(e){}
    const chart = new Chart(ctx, {
      type:'line',
      data:{ labels: opts.labels, datasets:[{
        label: opts.label||'', data: opts.data, borderColor: opts.borderColor, tension:0.35, pointRadius:0,
        fill:true,
        backgroundColor: function(context){
          const chart = context.chart, area = chart.chartArea;
          if(!area) return null;
          return createGradient(context.chart.ctx, area, opts.gradientColor || opts.borderColor);
        }
      }]},
      options:{ responsive:true, maintainAspectRatio:false, scales:{ x:{display:false}, y:{display:false, min:0, max:100} }, plugins:{ legend:{display:false}, tooltip:{mode:'index', intersect:false} } }
    });
    canvas._chart = chart;
    return chart;
  }

  function initCharts(){
    if(typeof Chart === 'undefined'){ setTimeout(initCharts,60); return; }
    const labels = Array.from({length:30},(_,i)=>i+1);
    diabetesChart = createOrUpdateLine('chart-diabetes-canvas',{ labels, data: randSeries(30,20,75), borderColor: (getComputedStyle(document.body).getPropertyValue('--accent')||'#0b5ecf').trim() });
    heartChart = createOrUpdateLine('chart-heart-canvas',{ labels, data: randSeries(30,10,70), borderColor:'#d9534f' });
    strokeChart = createOrUpdateLine('chart-stroke-canvas',{ labels, data: randSeries(30,5,60), borderColor:'#6f42c1' });

    if(diabetesChart) syncPanelWithChart(diabetesChart,'risk-diabetes','reasons-diabetes',['High HbA1c','Elevated fasting glucose','High BMI','Family history of diabetes','Certain medications']);
    if(heartChart) syncPanelWithChart(heartChart,'risk-heart','reasons-heart',['High LDL','Elevated systolic BP','ECG abnormality','Smoking','Diabetes']);
    if(strokeChart) syncPanelWithChart(strokeChart,'risk-stroke','reasons-stroke',['Chronic hypertension','Atrial fibrillation','Prior TIA','Smoking','High cholesterol']);
  }

  function updateCharts(){
    if(diabetesChart && diabetesChart.data && diabetesChart.data.datasets && diabetesChart.data.datasets[0]){
      diabetesChart.data.datasets[0].data = randSeries(30,20,80); diabetesChart.update();
    }
    if(heartChart && heartChart.data && heartChart.data.datasets && heartChart.data.datasets[0]){
      heartChart.data.datasets[0].data = randSeries(30,10,75); heartChart.update();
    }
    if(strokeChart && strokeChart.data && strokeChart.data.datasets && strokeChart.data.datasets[0]){
      strokeChart.data.datasets[0].data = randSeries(30,5,60); strokeChart.update();
    }
    if(diabetesChart) syncPanelWithChart(diabetesChart,'risk-diabetes','reasons-diabetes');
    if(heartChart) syncPanelWithChart(heartChart,'risk-heart','reasons-heart');
    if(strokeChart) syncPanelWithChart(strokeChart,'risk-stroke','reasons-stroke');
  }

  // expose if other pages want to call
  window.updateDashboardCharts = updateCharts;

  // ----------------------
  // In-page nav for first two buttons (Dashboard / Data Upload)
  // Exposed so the inline onclick="nav(this)" works.
  // ----------------------
  window.nav = function(btn){
    if(!btn) return;
    // find all .nav-link buttons (topnav)
    const topnav = btn.closest('.topnav');
    const all = topnav ? Array.from(topnav.querySelectorAll('.nav-link')) : [];

    // set active/aria-pressed
    all.forEach(n => {
      n.classList.remove('active');
      n.setAttribute('aria-pressed','false');
    });
    btn.classList.add('active');
    btn.setAttribute('aria-pressed','true');

    const target = btn.dataset ? btn.dataset.target : null;
    const sections = ['dashboard','upload'];
    sections.forEach(id => {
      const el = by(id);
      if(!el) return;
      el.style.display = (id === target) ? '' : 'none';
    });

    // if showing upload focus dropzone
    if(target === 'upload'){
      const dz = by('largeDropzone');
      if(dz) dz.focus();
    }else{
      // small UX: scroll to top of dashboard
      const dash = by('dashboard');
      if(dash) dash.scrollIntoView({behavior:'smooth', block:'start'});
    }
  };

  // ----------------------
  // Upload (in-page) logic — drag/drop + browse + CSV preview + summarize
  // ----------------------
  (function wireUpload(){
    const drop = by('largeDropzone');
    const fileInput = by('fileInput');
    const browseBtn = by('browseBtn');
    const preview = by('upload-preview');
    const analysisPreview = by('analysis-preview');
    const summaryEl = by('analysis-summary');
    const resultBtn = by('resultBtn'); // called 'resultBtn' in your HTML
    const manualLinkBtn = by('manualLinkBtn'); // inside upload section
    const openUploadBtn = by('openUpload'); // on dashboard action row
    const openManualBtn = by('openManual'); // dashboard action row

    const MAX = 20 * 1024 * 1024;
    let lastUploaded = null;

    function humanSize(b){
      if(b < 1024) return b + ' B';
      if(b < 1024*1024) return (b/1024).toFixed(1) + ' KB';
      return (b/(1024*1024)).toFixed(2) + ' MB';
    }

    function showPreviewText(txt, isErr){
      if(!preview) return;
      preview.textContent = txt;
      preview.style.color = isErr ? '#d9534f' : 'var(--muted)';
    }

    function resetAnalysis(){
      if(analysisPreview) analysisPreview.style.display = 'none';
      if(summaryEl) summaryEl.textContent = 'Results will appear here after uploading a file.';
      if(resultBtn) resultBtn.disabled = true;
      lastUploaded = null;
    }

    function finalize(name, message){
      if(summaryEl) summaryEl.innerHTML = `<strong>Key finding:</strong> ${message}`;
      try{ updateCharts(); }catch(e){}
    }

    function handleFileObject(file){
      resetAnalysis();
      if(!file){ showPreviewText('No file selected', true); return; }
      if(file.size > MAX){ showPreviewText(`File too large (${humanSize(file.size)}). Max ${humanSize(MAX)}.`, true); return; }
      lastUploaded = file;
      const name = file.name || 'file';
      const ext = (name.split('.').pop()||'').toLowerCase();
      showPreviewText(`Uploaded: ${name} · ${humanSize(file.size)}`);
      if(analysisPreview) analysisPreview.style.display = 'block';
      if(resultBtn) resultBtn.disabled = false;

      if(ext === 'csv' && FileReader){
        const reader = new FileReader();
        reader.onload = function(e){
          const text = e.target.result||'';
          const lines = text.split(/\r?\n/).filter(Boolean);
          const headers = lines.length ? lines[0].split(',').slice(0,12).map(h=>h.trim()) : [];
          summaryEl.textContent = `CSV detected — ${Math.max(lines.length-1,0)} rows (preview). Click Show Results to run quick analysis.`;
        };
        const blob = file.slice(0, 3000);
        reader.readAsText(blob);
        return;
      }

      summaryEl.textContent = `File uploaded: ${name}`;
    }

    function handleFileEvent(e){
      try{ e && e.preventDefault && e.preventDefault(); }catch(e){}
      const files = (e.target && e.target.files) || (e.dataTransfer && e.dataTransfer.files);
      if(!files || !files.length){ showPreviewText('No file dropped', true); return; }
      handleFileObject(files[0]);
    }

    // drag/drop
    if(drop){
      drop.addEventListener('dragover', function(e){ e.preventDefault(); drop.classList.add('dragover'); });
      drop.addEventListener('dragleave', function(){ drop.classList.remove('dragover'); });
      drop.addEventListener('drop', function(e){ e.preventDefault(); drop.classList.remove('dragover'); handleFileEvent(e); });
      drop.addEventListener('keydown', function(e){ if(e.key==='Enter'||e.key===' ') { e.preventDefault(); fileInput && fileInput.click(); }});
    }

    if(browseBtn && fileInput){
      browseBtn.addEventListener('click', ()=> fileInput.click());
      fileInput.addEventListener('change', handleFileEvent);
    }

    if(resultBtn){
      resultBtn.addEventListener('click', function(){
        if(!lastUploaded){
          showPreviewText('Please upload a file first (drag & drop or Browse files).', true);
          return;
        }
        if(analysisPreview) analysisPreview.style.display = 'block';
        summaryEl.textContent = 'Summarizing…';
        setTimeout(function(){
          finalize(lastUploaded.name, 'Simulated summary: elevated cardiometabolic risk; recommend targeted tests and follow-up.');
        }, 800 + Math.random()*600);
      });
    }

    // dashboard action buttons
    if(openUploadBtn){
      openUploadBtn.addEventListener('click', function(){
        // find the topnav Data Upload button and trigger nav
        const dataBtn = document.querySelector('.topnav .nav-link[data-target="upload"]');
        if(dataBtn) dataBtn.click();
        const el = by('upload');
        if(el) el.scrollIntoView({behavior:'smooth', block:'start'});
      });
    }

    // both manual link buttons navigate to manual.html
    function goManual(){
      window.location.href = 'manual.html';
    }
    if(openManualBtn) openManualBtn.addEventListener('click', goManual);
    if(manualLinkBtn) manualLinkBtn.addEventListener('click', goManual);

    // initialize
    resetAnalysis();
  })();

  // ----------------------
  // small UI bits: dropdowns & nav highlighting
  // ----------------------
  (function smallUi(){
    function toggleMenu(btnId, menuId){
      const btn = by(btnId), menu = by(menuId);
      if(!btn || !menu) return;
      btn.addEventListener('click', (e)=>{ e.stopPropagation(); const open = menu.style.display==='block'; menu.style.display = open ? 'none' : 'block'; menu.setAttribute('aria-hidden', open ? 'true' : 'false'); btn.setAttribute('aria-expanded', String(!open)); });
      qa(`#${menuId} .item`).forEach(it => it.addEventListener('click', ()=>{ const action = it.dataset.action||''; if(action==='signin') alert('Sign-in simulated'); else if(action==='switch') alert('Switch simulated'); else if(action==='signout') alert('Sign-out simulated'); menu.style.display='none'; btn.setAttribute('aria-expanded','false'); }));
    }
    toggleMenu('settingsToggle','settingsMenu');
    toggleMenu('authBox','authMenu');

    document.addEventListener('click', (e)=>{
      if(!e.target.closest('.dropdown')) { const sm = by('settingsMenu'); if(sm){ sm.style.display='none'; sm.setAttribute('aria-hidden','true'); } }
      if(!e.target.closest('.auth-container')) { const am = by('authMenu'); const ab = by('authBox'); if(am){ am.style.display='none'; am.setAttribute('aria-hidden','true'); } if(ab) ab.setAttribute('aria-expanded','false'); }
    });

    // topnav highlight for external links (advice/chat/report) and ensure active state for buttons remains correct
    function highlight(){
      qa('nav.topnav .nav-link').forEach(link=>{
        // for anchors, check href vs path
        if(link.tagName.toLowerCase() === 'a'){
          const href = (link.getAttribute('href') || '').split('/').pop();
          const path = location.pathname.split('/').pop() || 'user.html';
          if(href === path) link.classList.add('active'); else link.classList.remove('active');
        } else {
          // buttons will have active set by nav() when clicked — keep them as-is
        }
      });
    }
    highlight();
  })();

  // ----------------------
  // boot
  // ----------------------
  document.addEventListener('DOMContentLoaded', function(){
    initCharts();
    setTimeout(()=> { try{ updateCharts(); }catch(e){} }, 300);
  });

})(); // end IIFE
