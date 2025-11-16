/* style/js/app.js
   Final app JS for AutoCare — integrates charts, upload, chat/advice,
   and tidy/collapsible sidebar behavior with outside-click and ESC close.
*/

/* ---------- Utilities ---------- */
function by(id){ return document.getElementById(id); }
function qa(sel, root=document){ return Array.from((root||document).querySelectorAll(sel)); }

/* ---------- NAV ---------- */
function nav(btn){
  document.querySelectorAll('main.workspace section').forEach(s=>s.style.display='none');
  document.querySelectorAll('.topnav button').forEach(b=>b.classList.remove('active'));
  if(btn){ btn.classList.add('active'); }
  const target = btn && btn.dataset && btn.dataset.target;
  const section = target && document.getElementById(target);
  if(section) section.style.display = 'block';
  // when switching to chat/advice, open the appropriate sidebar
  if(target === 'chat') {
    // ensure chat sidebar expanded
    const chatSidebar = document.querySelector('#chat .sidebar');
    if(chatSidebar) setSidebarCollapsed(chatSidebar, false);
    // collapse adv sidebar
    const advSidebar = document.getElementById('advSidebar');
    if(advSidebar) setSidebarCollapsed(advSidebar, true);
  } else if(target === 'advice') {
    const advSidebar = document.getElementById('advSidebar');
    if(advSidebar) setSidebarCollapsed(advSidebar, false);
    const chatSidebar = document.querySelector('#chat .sidebar');
    if(chatSidebar) setSidebarCollapsed(chatSidebar, true);
  } else {
    // on other sections, collapse both sidebars
    const chatSidebar = document.querySelector('#chat .sidebar');
    const advSidebar = document.getElementById('advSidebar');
    if(chatSidebar) setSidebarCollapsed(chatSidebar, true);
    if(advSidebar) setSidebarCollapsed(advSidebar, true);
  }
  window.scrollTo({top:0,behavior:'smooth'});
}

/* ---------- Dropdown helpers (settings/auth) ---------- */
function toggleSettings(ev){
  ev && ev.stopPropagation();
  const menu = by('settingsMenu');
  if(!menu) return;
  const isOpen = menu.style.display === 'block';
  menu.style.display = isOpen ? 'none' : 'block';
  menu.setAttribute('aria-hidden', isOpen ? 'true' : 'false');
}
function closeSettings(){ const menu = by('settingsMenu'); if(menu){ menu.style.display='none'; menu.setAttribute('aria-hidden','true'); } }
function toggleAuthMenu(ev){
  ev && ev.stopPropagation();
  const menu = by('authMenu'); const box = by('authBox');
  if(!menu || !box) return;
  const isOpen = menu.style.display === 'block';
  menu.style.display = isOpen ? 'none' : 'block';
  menu.setAttribute('aria-hidden', isOpen ? 'true' : 'false');
  box.setAttribute('aria-expanded', String(!isOpen));
}
function closeAuthMenu(){ const menu = by('authMenu'); const box = by('authBox'); if(menu){ menu.style.display='none'; menu.setAttribute('aria-hidden','true'); } if(box) box.setAttribute('aria-expanded','false'); }

/* ---------- Charts & Panels ---------- */
let diabetesChart, heartChart, strokeChart;

function hexToRgba(hex, alpha){
  if(!hex) return 'rgba(11,94,207,'+alpha+')';
  hex = hex.replace('#','').trim();
  if(hex.length === 3) hex = hex.split('').map(c=>c+c).join('');
  const bigint = parseInt(hex,16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  return 'rgba('+r+','+g+','+b+','+alpha+')';
}

function randomSeries(n,min,max){
  const a=[];
  for(let i=0;i<n;i++) a.push(Math.floor(Math.random()*(max-min)+min));
  return a;
}

function computeRiskFromData(arr){
  if(!arr || !arr.length) return 0;
  const avg = arr.reduce((s,v)=>s+v,0)/arr.length;
  return Math.round(avg);
}
function riskClass(percent){
  if(percent >= 70) return 'risk-high';
  if(percent >= 40) return 'risk-mid';
  return 'risk-low';
}

function syncPanelWithChart(chart, riskElId, reasonsElId, featureCandidates){
  try{
    const data = chart.data.datasets[0].data;
    const risk = computeRiskFromData(data);
    const riskEl = by(riskElId);
    if(riskEl){ riskEl.textContent = risk + '%'; riskEl.className = 'risk-badge '+ riskClass(risk); }

    const reasonsEl = by(reasonsElId);
    if(!reasonsEl) return;

    const features = (featureCandidates && featureCandidates.length) ? featureCandidates.slice() : ['Elevated lab value','Abnormal vitals','Relevant med history','Imaging flag','Age/comorbidity'];
    const last = data[data.length-1] || 0;
    const mid = data[Math.floor(data.length/2)] || 0;
    const variance = Math.round(Math.abs(last - mid)) || 5;

    const scored = features.map((f,i)=>({f,score: Math.round((Math.random()*20) + (last/3) - (i*2) + variance/3)}));
    scored.sort((a,b)=>b.score-a.score);

    let html = '';
    for(let i=0;i<Math.min(5,scored.length);i++){
      const item = scored[i];
      const short = item.f;
      const detail = `relative importance ${item.score}`;
      const color = i===0 ? (getComputedStyle(document.body).getPropertyValue('--accent').trim() || '#0b5ecf') : (i===1 ? '#d9534f' : (i===2 ? '#6f42c1' : '#b0b0b0'));
      html += `<li><span class="dot" style="background:${color}"></span><div class="reason-text">${short}<span class="reason-sub">${detail}</span></div></li>`;
    }
    reasonsEl.innerHTML = html;
  }catch(e){ console.warn('syncPanelWithChart error',e); }
}

function initCharts(){
  if(typeof Chart === 'undefined') return;
  Chart.defaults.font.family = "'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue'";
  Chart.defaults.font.size = 12;
  Chart.defaults.color = getComputedStyle(document.body).getPropertyValue('--muted') || '#586068';

  function createGradient(ctx, area, color){
    const g = ctx.createLinearGradient(0,0,0,area.bottom);
    g.addColorStop(0, hexToRgba(color,0.20));
    g.addColorStop(1, hexToRgba(color,0.02));
    return g;
  }

  // Diabetes
  const dCtxEl = by('chart-diabetes-canvas');
  if(dCtxEl){
    const dCtx = dCtxEl.getContext('2d');
    diabetesChart = new Chart(dCtx, {
      type: 'line',
      data: {
        labels: Array.from({length:30}, (_, i) => i + 1),
        datasets: [{
          label: 'Diabetes risk (%)',
          data: randomSeries(30, 20, 75),
          borderColor: (getComputedStyle(document.body).getPropertyValue('--accent') || '#0b5ecf').trim(),
          tension: 0.35,
          pointRadius: 0,
          fill: true,
          backgroundColor: function(context) {
            const chart = context.chart; const ctx = chart.ctx; const chartArea = chart.chartArea;
            if (!chartArea) return null;
            const accent = (getComputedStyle(document.body).getPropertyValue('--accent') || '#0b5ecf').trim();
            return createGradient(ctx, chartArea, accent);
          }
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: { x: { display: false }, y: { display: false, min: 0, max: 100 } },
        plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false } }
      }
    });
  }

  // Heart
  const hCtxEl = by('chart-heart-canvas');
  if(hCtxEl){
    const hCtx = hCtxEl.getContext('2d');
    heartChart = new Chart(hCtx, {
      type:'line',
      data:{ labels: Array.from({length:30},(_,i)=>i+1), datasets:[{ label:'Heart risk (%)', data: randomSeries(30,10,70), borderColor: '#d9534f', tension:0.35, pointRadius:0, fill:true, backgroundColor: function(context){ const chart = context.chart; const {ctx, chartArea} = chart; if(!chartArea) return null; return createGradient(ctx, chartArea, '#d9534f'); } }] },
      options:{ responsive:true, maintainAspectRatio:false, scales:{ x:{ display:false}, y:{ display:false, min:0, max:100 } }, plugins:{ legend:{ display:false }, tooltip:{ mode:'index', intersect:false } } }
    });
  }

  // Stroke
  const sCtxEl = by('chart-stroke-canvas');
  if(sCtxEl){
    const sCtx = sCtxEl.getContext('2d');
    strokeChart = new Chart(sCtx, {
      type:'line',
      data:{ labels: Array.from({length:30},(_,i)=>i+1), datasets:[{ label:'Stroke risk (%)', data: randomSeries(30,5,60), borderColor: '#6f42c1', tension:0.35, pointRadius:0, fill:true, backgroundColor: function(context){ const chart = context.chart; const {ctx, chartArea} = chart; if(!chartArea) return null; return createGradient(ctx, chartArea, '#6f42c1'); } }] },
      options:{ responsive:true, maintainAspectRatio:false, scales:{ x:{ display:false}, y:{ display:false, min:0, max:100 } }, plugins:{ legend:{ display:false }, tooltip:{ mode:'index', intersect:false } } }
    });
  }

  if(diabetesChart) syncPanelWithChart(diabetesChart,'risk-diabetes','reasons-diabetes', ['High HbA1c','Elevated fasting glucose','High BMI','Family history of diabetes','Certain medications']);
  if(heartChart) syncPanelWithChart(heartChart,'risk-heart','reasons-heart', ['High LDL cholesterol','Elevated systolic blood pressure','ECG abnormalities','Smoking history','Diabetes']);
  if(strokeChart) syncPanelWithChart(strokeChart,'risk-stroke','reasons-stroke', ['Chronic hypertension','Atrial fibrillation flagged','Prior TIA','Smoking','High cholesterol']);
}

function updateCharts(){
  if(diabetesChart){ diabetesChart.data.datasets[0].data = randomSeries(30,20,80); diabetesChart.update(); }
  if(heartChart){ heartChart.data.datasets[0].data = randomSeries(30,10,75); heartChart.update(); }
  if(strokeChart){ strokeChart.data.datasets[0].data = randomSeries(30,5,60); strokeChart.update(); }
  if(diabetesChart) syncPanelWithChart(diabetesChart,'risk-diabetes','reasons-diabetes');
  if(heartChart) syncPanelWithChart(heartChart,'risk-heart','reasons-heart');
  if(strokeChart) syncPanelWithChart(strokeChart,'risk-stroke','reasons-stroke');
}

/* ---------- Upload drag/drop ---------- */
function wireUpload(){
  const largeDropzone = by('largeDropzone');
  if(!largeDropzone) return;
  largeDropzone.addEventListener('dragover', e=>{ e.preventDefault(); largeDropzone.classList.add('dragover'); });
  largeDropzone.addEventListener('dragleave', e=>{ largeDropzone.classList.remove('dragover'); });
  largeDropzone.addEventListener('drop', e=>{ e.preventDefault(); largeDropzone.classList.remove('dragover'); handleFile({target:{files:e.dataTransfer.files}}); });
  largeDropzone.addEventListener('keydown', e=>{ if(e.key === 'Enter'){ const fi = by('fileInput'); if(fi) fi.click(); } });

  const fileInput = by('fileInput');
  if(fileInput) fileInput.addEventListener('change', handleFile);

  const browseBtn = by('browseBtn');
  if(browseBtn) browseBtn.addEventListener('click', ()=>{ fileInput && fileInput.click(); });
}
function handleFile(event){
  const file = event.target.files && event.target.files[0];
  if(!file) return;
  const up = by('upload-preview'); if(up) up.innerText = `Uploaded: ${file.name} — running analysis...`;
  const ap = by('analysis-preview'); if(ap) ap.style.display = 'block';
  const summary = by('analysis-summary'); if(summary) summary.innerText = 'Summary: Processing complete. Click Show Results to reveal the detailed panel.';
  const resultBtn = by('resultBtn'); if(resultBtn){ resultBtn.disabled = false; resultBtn.focus(); }
  updateCharts();
}

/* ---------- Reports / misc ---------- */
function generateReport(){ alert('Report generated (simulated).'); }
function downloadReport(){ alert('Download initiated (simulated).'); }
function openManualPage(){ alert('Open manual-entry page (simulated)'); }

/* ---------- Account placeholders ---------- */
function simulateSignIn(){ const sa = by('settings-account'); if(sa) sa.innerText = 'Dr. User'; alert('Sign-in simulated'); closeAuthMenu(); closeSettings(); }
function simulateSwitch(){ const sa = by('settings-account'); if(sa) sa.innerText = 'Nurse A'; alert('Switch account simulated'); closeAuthMenu(); closeSettings(); }
function simulateSignOut(){ const sa = by('settings-account'); if(sa) sa.innerText = 'Guest'; alert('Signed out (simulated)'); closeAuthMenu(); closeSettings(); }

/* ---------- Sidebar collapse helpers (chat + advice) ---------- */
function setSidebarCollapsed(sidebarEl, collapsed){
  if(!sidebarEl) return;
  if(collapsed){
    sidebarEl.classList.add('collapsed');
    sidebarEl.setAttribute('aria-hidden','true');
  } else {
    sidebarEl.classList.remove('collapsed');
    sidebarEl.setAttribute('aria-hidden','false');
  }
}

function toggleChatSidebar(){
  const chatSidebar = document.querySelector('#chat .sidebar');
  const advSidebar = document.getElementById('advSidebar');
  if(!chatSidebar) return;
  const isCollapsed = chatSidebar.classList.toggle('collapsed');
  chatSidebar.setAttribute('aria-hidden', isCollapsed ? 'true' : 'false');
  const btn = by('polToggleSidebar'); if(btn) btn.setAttribute('aria-pressed', String(!isCollapsed));
  // if chat opened, collapse advice
  if(!isCollapsed && advSidebar) setSidebarCollapsed(advSidebar, true);
}

function toggleAdvSidebar(){
  const advSidebar = document.getElementById('advSidebar');
  const chatSidebar = document.querySelector('#chat .sidebar');
  if(!advSidebar) return;
  const isCollapsed = advSidebar.classList.toggle('collapsed');
  advSidebar.setAttribute('aria-hidden', isCollapsed ? 'true' : 'false');
  const btn = by('advToggleBtn'); if(btn) btn.setAttribute('aria-pressed', String(!isCollapsed));
  // if advice opened, collapse chat
  if(!isCollapsed && chatSidebar) setSidebarCollapsed(chatSidebar, true);
}

function closeBothSidebarsIfOpen(e){
  // if click inside sidebars or on their toggles, do nothing
  if(e && (e.target.closest && (e.target.closest('#chat .sidebar') || e.target.closest('#advSidebar') || e.target.closest('#polToggleSidebar') || e.target.closest('#advToggleBtn') || e.target.closest('.topnav button[data-target="chat"]') || e.target.closest('.topnav button[data-target="advice"]')))){
    return;
  }
  const chatSidebar = document.querySelector('#chat .sidebar');
  const advSidebar = document.getElementById('advSidebar');
  if(chatSidebar && !chatSidebar.classList.contains('collapsed')) setSidebarCollapsed(chatSidebar, true);
  if(advSidebar && !advSidebar.classList.contains('collapsed')) setSidebarCollapsed(advSidebar, true);
  const polBtn = by('polToggleSidebar'); if(polBtn) polBtn.setAttribute('aria-pressed','false');
  const advBtn = by('advToggleBtn'); if(advBtn) advBtn.setAttribute('aria-pressed','false');
}

/* Wire sidebar handlers */
function wireSidebarBehavior(){
  const polToggle = by('polToggleSidebar');
  if(polToggle) polToggle.addEventListener('click', (ev)=>{ ev.stopPropagation(); toggleChatSidebar(); });

  const advToggle = by('advToggleBtn');
  if(advToggle) advToggle.addEventListener('click', (ev)=>{ ev.stopPropagation(); toggleAdvSidebar(); });

  // close sidebars when clicking outside
  document.addEventListener('click', (e)=>{ closeBothSidebarsIfOpen(e); });

  // ESC to close
  document.addEventListener('keydown', (e)=>{ if(e.key === 'Escape') closeBothSidebarsIfOpen(); });
}

/* ---------- Polished Chat ---------- */
function initPolishedChat(){
  const userInput = by('polUserInput');
  const sendBtn = by('polSendBtn');
  const messages = by('polMessages');
  const chatList = by('polChatList');
  const newChatBtn = by('polNewChat');

  function timeNow(){ const d = new Date(); return d.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}); }
  function escapeHtml(unsafe){ return String(unsafe || '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;'); }

  userInput && userInput.focus();

  function addMessage(text, role='assistant'){
    const el = document.createElement('div');
    el.className = 'msg ' + (role === 'user' ? 'user' : 'assistant');
    const meta = document.createElement('div'); meta.className = 'meta'; meta.textContent = role === 'user' ? 'You' : 'Assistant';
    const body = document.createElement('div'); body.innerHTML = escapeHtml(text).replace(/\n/g,'<br>');
    const tm = document.createElement('div'); tm.className = 'time'; tm.textContent = timeNow();
    el.appendChild(meta); el.appendChild(body); el.appendChild(tm);
    messages.appendChild(el);
    el.scrollIntoView({behavior:'smooth', block:'end'});
  }

  async function postData(url = "", data = {}){
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if(!response.ok) throw new Error('Network response not ok: ' + response.status);
      return await response.json();
    } catch(e){
      return { answer: mockReply(data.question) };
    }
  }

  function mockReply(q){
    const ql = String(q || '').toLowerCase();
    if(ql.includes('upload')) return 'To upload, go to Data Upload → Browse files or drag & drop a CSV/PDF. Then click Show Results.';
    if(ql.includes('report')) return 'Click Reports → Generate PDF to create a downloadable report (simulated).';
    if(ql.includes('risk')) return 'Risk is displayed on dashboard cards (Diabetes / Heart / Stroke). Run Show Results after upload.';
    return "Demo reply: replace /api with your backend for real responses.";
  }

  async function sendMessage(){
    const text = (userInput && userInput.value || '').trim();
    if(!text) return;
    addMessage(text, 'user');
    userInput.value = '';
    const placeholder = document.createElement('div');
    placeholder.className = 'msg assistant';
    placeholder.innerHTML = '<div class="meta">Assistant</div><div>Thinking <span class="typing"><span></span><span></span><span></span></span></div>';
    messages.appendChild(placeholder);
    placeholder.scrollIntoView({behavior:'smooth', block:'end'});

    try {
      const result = await postData('/api', { question: text });
      placeholder.remove();
      const ans = (result && result.answer) ? String(result.answer) : 'No answer.';
      addMessage(ans, 'assistant');

      const item = document.createElement('div');
      item.className = 'chat-item';
      item.setAttribute('data-q', text);
      item.innerHTML = '<div class="icon" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="1.1"/></svg></div>'
        + '<div class="title">' + escapeHtml(text) + '</div>';
      chatList.prepend(item);
    } catch(err){
      placeholder.remove();
      addMessage('Error: ' + (err.message || 'Something went wrong'), 'assistant');
      console.error(err);
    }
  }

  sendBtn && sendBtn.addEventListener('click', (e)=>{ e.preventDefault(); sendMessage(); });
  userInput && userInput.addEventListener('keydown', (e)=>{ if(e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); sendMessage(); } });
  newChatBtn && newChatBtn.addEventListener('click', ()=>{ messages.innerHTML = ''; userInput.value = ''; userInput.focus(); });

  // click conversation history to reuse query
  document.addEventListener('click', (e)=>{
    const it = e.target.closest('.chat-item');
    if(it){
      const q = it.getAttribute('data-q') || '';
      if(userInput) userInput.value = q;
      userInput && userInput.focus();
    }
  });
}

/* ---------- Polished Advice ---------- */
function initPolishedAdvice(){
  const sidebar = by('advSidebar');
  const toggleBtn = by('advToggleBtn');
  const history = by('advHistory');
  const advMessages = by('advMessages');
  const advInput = by('advInput');
  const advSendBtn = by('advSendBtn');
  const advRunBtn = by('advRunAssessment');
  const advEditCtx = by('advEditContext');

  if(toggleBtn && sidebar){
    toggleBtn.addEventListener('click', (e)=>{
      e.stopPropagation();
      toggleAdvSidebar();
    });
  }

  if(history){
    history.addEventListener('click', (e)=>{
      const it = e.target.closest('.adv-item');
      if(!it) return;
      const q = it.getAttribute('data-q') || '';
      advInput && (advInput.value = q);
      advInput && advInput.focus();
    });
  }

  function mockAdviceReply(q){
    const ql = String(q || '').toLowerCase();
    if(ql.includes('assessment') || ql.includes('run')) return 'Quick assessment: BP elevated, consider home BP monitoring and review antihypertensives. Recommend follow-up in 2 weeks.';
    if(ql.includes('lipid')) return 'Lipid guidance: consider high-intensity statin if ASCVD risk >20% and LDL > 70 mg/dL. Check LFTs baseline.';
    if(ql.includes('diabetes')) return 'Diabetes plan: suggest HbA1c, optimize metformin dose, recommend lifestyle referral. Consider SGLT2 if CV disease present.';
    return 'This is an advice demo. Connect a backend or knowledge source for evidence-cited recommendations.';
  }

  function addAdvMessage(text, role='assistant'){
    const el = document.createElement('div');
    el.className = 'adv-msg ' + (role === 'user' ? 'user' : 'assistant');
    const meta = document.createElement('div'); meta.className = 'meta'; meta.textContent = role === 'user' ? 'You' : 'Assistant';
    const body = document.createElement('div'); body.innerHTML = text.replace(/\n/g,'<br>');
    el.appendChild(meta); el.appendChild(body);
    advMessages.appendChild(el);
    el.scrollIntoView({behavior:'smooth', block:'end'});
  }

  async function sendAdvice(){
    const q = advInput && advInput.value.trim();
    if(!q) return;
    addAdvMessage(q, 'user');
    advInput.value = '';

    const placeholder = document.createElement('div');
    placeholder.className = 'adv-msg assistant';
    placeholder.innerHTML = '<div class="meta">Assistant</div><div>Thinking <span class="typing"><span></span><span></span><span></span></span></div>';
    advMessages.appendChild(placeholder);
    placeholder.scrollIntoView({behavior:'smooth', block:'end'});

    setTimeout(()=>{
      placeholder.remove();
      const ans = mockAdviceReply(q);
      addAdvMessage(ans, 'assistant');

      const item = document.createElement('div');
      item.className = 'adv-item';
      item.setAttribute('data-q', q);
      item.innerHTML = '<div class="icon" aria-hidden="true" style="width:36px;height:36;border-radius:8px;display:flex;align-items:center;justify-content:center;background:#f3f6fb;border:1px solid var(--line);color:var(--accent)">•</div>'
        + '<div class="title">' + (q.length > 42 ? q.slice(0,40) + '…' : q) + '</div>';
      history.prepend(item);
    }, 600 + Math.random()*400);
  }

  if(advRunBtn){
    advRunBtn.addEventListener('click', ()=>{
      addAdvMessage('Running quick assessment...', 'user');
      setTimeout(()=>{
        addAdvMessage('Quick assessment: Estimated 10-year ASCVD risk ~18%. Recommend statin initiation and BP control. Order HbA1c and fasting lipid panel.', 'assistant');
      }, 800);
    });
  }

  if(advEditCtx){
    advEditCtx.addEventListener('click', ()=>{
      const newName = prompt('Edit patient name (demo):', 'Mr. A. Kumar');
      if(newName){
        const nameEl = document.querySelector('#advice .adv-summary .name');
        if(nameEl) nameEl.textContent = 'Patient: ' + newName;
      }
    });
  }

  const advToggleSummary = by('advToggleSummary');
  if(advToggleSummary){
    advToggleSummary.addEventListener('click', ()=>{
      const upper = document.querySelector('#advice .adv-upper');
      if(upper){
        if(upper.style.display === 'none'){
          upper.style.display = 'flex';
          advToggleSummary.textContent = '▲';
        } else {
          upper.style.display = 'none';
          advToggleSummary.textContent = '▼';
        }
      }
    });
  }

  advSendBtn && advSendBtn.addEventListener('click', (e)=>{ e.preventDefault(); sendAdvice(); });
  advInput && advInput.addEventListener('keydown', (e)=>{ if(e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); sendAdvice(); } });

  advInput && advInput.focus();
}

/* ---------- Wire everything in DOMContentLoaded ---------- */
document.addEventListener('DOMContentLoaded', ()=>{
  // default nav to dashboard
  const dashBtn = document.querySelector('.topnav button[data-target="dashboard"]');
  if(dashBtn) dashBtn.click();

  // wire small UI pieces
  wireUpload();
  initCharts();
  initPolishedChat();
  initPolishedAdvice();
  wireSidebarBehavior();

  // settings/auth toggles + global close handler
  const settingsToggle = by('settingsToggle');
  if(settingsToggle) settingsToggle.addEventListener('click', toggleSettings);
  document.addEventListener('click', (e)=>{
    if(!e.target.closest('.dropdown')) closeSettings();
  });

  const authBox = by('authBox');
  if(authBox) authBox.addEventListener('click', toggleAuthMenu);
  document.addEventListener('click', (e)=>{
    if(!e.target.closest('.auth-container')) closeAuthMenu();
  });

  // simulate dropdown actions
  qa('.dropdown-menu .item').forEach(item=>{
    item.addEventListener('click', (e)=>{
      const action = item.dataset.action || '';
      if(action === 'signin'){ simulateSignIn(); }
      else if(action === 'switch'){ simulateSwitch(); }
      else if(action === 'signout'){ simulateSignOut(); }
    });
  });

  // wire small buttons
  const openManual = by('openManual');
  if(openManual) openManual.addEventListener('click', openManualPage);
  const resultBtn = by('resultBtn');
  if(resultBtn) resultBtn.addEventListener('click', showResults);
  const genReport = by('genReport');
  if(genReport) genReport.addEventListener('click', generateReport);
  const dlReport = by('dlReport');
  if(dlReport) dlReport.addEventListener('click', downloadReport);

  // collapse sidebars by default for tidy UI
  const chatSidebar = document.querySelector('#chat .sidebar');
  const advSidebar = by('advSidebar');
  if(chatSidebar) setSidebarCollapsed(chatSidebar, true);
  if(advSidebar) setSidebarCollapsed(advSidebar, true);

  // ensure topnav chat/advice open sections also open their sidebars
  qa('.topnav button').forEach(btn=>{
    btn.addEventListener('click', (e)=>{
      const target = btn.dataset.target;
      if(target === 'chat'){
        const cs = document.querySelector('#chat .sidebar'); if(cs) setSidebarCollapsed(cs, false);
        const as = by('advSidebar'); if(as) setSidebarCollapsed(as, true);
      } else if(target === 'advice'){
        const as = by('advSidebar'); if(as) setSidebarCollapsed(as, false);
        const cs = document.querySelector('#chat .sidebar'); if(cs) setSidebarCollapsed(cs, true);
      } else {
        // collapse both for other views
        const cs = document.querySelector('#chat .sidebar'); if(cs) setSidebarCollapsed(cs, true);
        const as = by('advSidebar'); if(as) setSidebarCollapsed(as, true);
      }
    });
  });
});

/* ---------- Small: showResults triggers chart update ---------- */
function showResults(){
  updateCharts();
  const analysisSummary = by('analysis-summary');
  if(analysisSummary) analysisSummary.innerHTML = '<strong>Key findings:</strong> Simulated cohort shows elevated cardiometabolic risk — recommend follow-up testing.';
  const rb = by('resultBtn'); if(rb) rb.disabled = false;
}

/* ---------- End of file ---------- */
