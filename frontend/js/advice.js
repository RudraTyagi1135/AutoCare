// js/advice.js
// Advice page behavior: history, compose, quick assessment, edit context

(function(){
  function by(id){ return document.getElementById(id); }
  function timeNow(){ const d=new Date(); return d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}); }

  function mockAdviceReply(q){
    const ql = String(q || '').toLowerCase();
    if(ql.includes('assessment') || ql.includes('run')) return 'Quick assessment: BP elevated; consider meds review and home BP monitoring.';
    if(ql.includes('lipid')) return 'Lipid guidance: consider statin intensity per ASCVD risk; check baseline LFTs.';
    if(ql.includes('diabetes')) return 'Diabetes plan: check HbA1c; optimise metformin; lifestyle referral.';
    return 'Advice demo — connect a clinical knowledge base for evidence-backed recommendations.';
  }

  function addAdvMessage(messagesEl, text, role='assistant'){
    const el = document.createElement('div');
    el.className = 'adv-msg ' + (role === 'user' ? 'user' : 'assistant');
    const meta = document.createElement('div'); meta.className = 'meta';
    meta.textContent = role === 'user' ? 'You' : 'Assistant';
    const body = document.createElement('div'); body.innerHTML = String(text).replace(/\n/g,'<br>');
    el.appendChild(meta); el.appendChild(body);
    messagesEl.appendChild(el);
    el.scrollIntoView({behavior:'smooth', block:'end'});
  }

  async function initPolishedAdvice(){
    const sidebar = by('advSidebar');
    const toggleBtn = by('advToggleBtn');
    const history = by('advHistory');
    const advMessages = by('advMessages');
    const advInput = by('advInput');
    const advSendBtn = by('advSendBtn');
    const advRunBtn = by('advRunAssessment');
    const advEditCtx = by('advEditContext');

    if(!advMessages || !advInput) return;

    // history click: populate question
    history && history.addEventListener('click', (e)=>{
      const it = e.target.closest('.adv-item');
      if(!it) return;
      const q = it.getAttribute('data-q') || '';
      advInput && (advInput.value = q);
      advInput && advInput.focus();
    });

    if(toggleBtn && sidebar){
      toggleBtn.addEventListener('click', (ev)=>{ ev.stopPropagation(); const isCollapsed = sidebar.classList.toggle('collapsed'); sidebar.setAttribute('aria-hidden', String(isCollapsed)); toggleBtn.setAttribute('aria-pressed', String(!isCollapsed)); });
    }

    advSendBtn && advSendBtn.addEventListener('click', async (e)=>{
      e.preventDefault();
      const q = advInput.value.trim();
      if(!q) return;
      addAdvMessage(advMessages, q, 'user');
      advInput.value = '';
      const placeholder = document.createElement('div');
      placeholder.className = 'adv-msg assistant';
      placeholder.innerHTML = '<div class="meta">Assistant</div><div>Thinking <span class="typing"><span></span><span></span><span></span></span></div>';
      advMessages.appendChild(placeholder);
      placeholder.scrollIntoView({behavior:'smooth', block:'end'});

      // simulated processing
      setTimeout(()=>{
        placeholder.remove();
        const ans = mockAdviceReply(q);
        addAdvMessage(advMessages, ans, 'assistant');
        // add to history
        if(history){
          const item = document.createElement('div');
          item.className = 'adv-item';
          item.setAttribute('data-q', q);
          item.innerHTML = '<div class="icon" aria-hidden="true" style="width:36px;height:36;border-radius:8px;display:flex;align-items:center;justify-content:center;background:#f3f6fb;border:1px solid var(--line);color:var(--accent)">•</div>'
            + '<div class="title">' + (q.length>42 ? q.slice(0,40)+'…' : q) + '</div>';
          history.prepend(item);
        }
      }, 600 + Math.random()*400);
    });

    advInput && advInput.addEventListener('keydown', (e)=>{ if(e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); advSendBtn && advSendBtn.click(); } });

    if(advRunBtn){
      advRunBtn.addEventListener('click', ()=>{
        addAdvMessage(advMessages, 'Running quick assessment...', 'user');
        setTimeout(()=> addAdvMessage(advMessages, 'Quick assessment: estimated elevated ASCVD risk. Recommend statin and BP review.', 'assistant'), 800);
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

    advInput.focus();
  }

  // expose save hook
  window.saveFragmentState = function(){
    return {
      draft: by('advInput')?.value || '',
      html: by('advMessages')?.innerHTML || ''
    };
  };

  document.addEventListener('DOMContentLoaded', initPolishedAdvice);
  window.initPolishedAdvice = initPolishedAdvice;
})();
