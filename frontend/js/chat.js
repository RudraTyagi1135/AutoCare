// js/chat.js
// Chat page behavior: conversation UI, sendMessage, mock fallback

(function(){
  function by(id){ return document.getElementById(id); }
  function qa(sel, root=document){ return Array.from((root||document).querySelectorAll(sel)); }

  function timeNow(){
    const d = new Date();
    return d.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
  }
  function escapeHtml(unsafe){
    return String(unsafe || '')
      .replaceAll('&','&amp;')
      .replaceAll('<','&lt;')
      .replaceAll('>','&gt;')
      .replaceAll('"','&quot;')
      .replaceAll("'",'&#039;');
  }

  async function postData(url="", data={}){
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type':'application/json' },
        body: JSON.stringify(data)
      });
      if(!res.ok) throw new Error('Network response not ok: '+res.status);
      return await res.json();
    } catch(e){
      return { answer: mockReply(data.question) };
    }
  }

  function mockReply(q){
    const ql = String(q || '').toLowerCase();
    if(ql.includes('upload')) return 'To upload, use Data Upload. Drag & drop or Browse files.';
    if(ql.includes('report')) return 'Use Reports → Generate PDF to create a report.';
    if(ql.includes('risk')) return 'Risks appear on the Dashboard cards after analysis.';
    return 'Demo reply: replace with your backend /api for real responses.';
  }

  function addMessage(messagesEl, text, role='assistant'){
    const el = document.createElement('div');
    el.className = 'msg ' + (role==='user' ? 'user' : 'assistant');
    const meta = document.createElement('div'); meta.className = 'meta';
    meta.textContent = role === 'user' ? 'You' : 'Assistant';
    const body = document.createElement('div');
    body.innerHTML = escapeHtml(text).replace(/\n/g,'<br>');
    const tm = document.createElement('div'); tm.className = 'time'; tm.textContent = timeNow();
    el.appendChild(meta); el.appendChild(body); el.appendChild(tm);
    messagesEl.appendChild(el);
    el.scrollIntoView({ behavior:'smooth', block:'end' });
  }

  async function initPolishedChat(){
    const userInput = by('polUserInput');
    const sendBtn = by('polSendBtn');
    const messages = by('polMessages');
    const chatList = by('polChatList');
    const newChatBtn = by('polNewChat');

    if(!messages || !userInput) return;

    userInput.focus();

    async function sendMessage(){
      const text = (userInput.value || '').trim();
      if(!text) return;
      addMessage(messages, text, 'user');
      userInput.value = '';

      // placeholder while fetching
      const placeholder = document.createElement('div');
      placeholder.className = 'msg assistant';
      placeholder.innerHTML = '<div class="meta">Assistant</div><div>Thinking <span class="typing"><span></span><span></span><span></span></span></div>';
      messages.appendChild(placeholder);
      placeholder.scrollIntoView({ behavior:'smooth', block:'end' });

      try {
        const result = await postData('/api', { question: text });
        placeholder.remove();
        const ans = (result && (result.answer || result.reply)) ? (result.answer || result.reply) : 'No answer.';
        addMessage(messages, ans, 'assistant');

        // add to conversation list
        if(chatList){
          const item = document.createElement('div');
          item.className = 'chat-item';
          item.setAttribute('data-q', text);
          item.innerHTML = '<div class="icon" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="1.1"/></svg></div>'
            + '<div class="title">' + escapeHtml(text) + '</div>';
          chatList.prepend(item);
        }

      } catch(err){
        placeholder.remove();
        addMessage(messages, 'Error: ' + (err.message || 'Something went wrong'), 'assistant');
        console.error(err);
      }
    }

    sendBtn && sendBtn.addEventListener('click', (e)=>{ e.preventDefault(); sendMessage(); });
    userInput.addEventListener('keydown', (e)=>{ if(e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); sendMessage(); } });

    newChatBtn && newChatBtn.addEventListener('click', ()=>{
      messages.innerHTML = '';
      if(userInput) userInput.value = '';
      userInput.focus();
    });

    // reuse queries from history
    document.addEventListener('click', (e)=>{
      const it = e.target.closest('.chat-item');
      if(it){
        const q = it.getAttribute('data-q') || '';
        if(userInput) userInput.value = q;
        userInput && userInput.focus();
      }
    });
  }

  // Auto-init if loaded direct
  document.addEventListener('DOMContentLoaded', initPolishedChat);
  // export
  window.initPolishedChat = initPolishedChat;
})();
