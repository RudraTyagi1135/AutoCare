// js/chat.js
// Chat page → connects to GENERAL chatbot: /api/chat/general

(function(){
  function by(id){ return document.getElementById(id); }

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

  // REAL backend call
  async function callGeneralChat(question){
    try {
      const res = await fetch("/api/chat/general", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message: question })
      });

      return await res.json();
    } catch (e){
      return { reply: "⚠️ Backend error. Check server." };
    }
  }

  function addMessage(messagesEl, text, role='assistant'){
    const el = document.createElement('div');
    el.className = 'msg ' + (role==='user' ? 'user' : 'assistant');

    const meta = document.createElement('div');
    meta.className = 'meta';
    meta.textContent = role === 'user' ? 'You' : 'Assistant';

    const body = document.createElement('div');
    body.innerHTML = escapeHtml(text).replace(/\n/g,'<br>');

    const tm = document.createElement('div');
    tm.className = 'time';
    tm.textContent = timeNow();

    el.appendChild(meta);
    el.appendChild(body);
    el.appendChild(tm);

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

      // Loading bubble
      const placeholder = document.createElement('div');
      placeholder.className = 'msg assistant';
      placeholder.innerHTML =
        '<div class="meta">Assistant</div>' +
        '<div>Thinking <span class="typing"><span></span><span></span><span></span></span></div>' +
        '<div class="time">--</div>';
      messages.appendChild(placeholder);
      placeholder.scrollIntoView({ behavior:'smooth', block:'end' });

      // REAL API CALL
      const response = await callGeneralChat(text);

      placeholder.remove();
      const answer = response.reply || "No reply from server.";
      addMessage(messages, answer, 'assistant');

      // add to left sidebar history
      if(chatList){
        const item = document.createElement('div');
        item.className = 'chat-item';
        item.setAttribute('data-q', text);
        item.innerHTML =
          '<div class="icon"></div>' +
          '<div class="title">' + escapeHtml(text) + '</div>';
        chatList.prepend(item);
      }
    }

    sendBtn.addEventListener('click', (e)=>{ e.preventDefault(); sendMessage(); });
    userInput.addEventListener('keydown', (e)=>{ 
      if(e.key === 'Enter' && !e.shiftKey){ 
        e.preventDefault(); sendMessage(); 
      }
    });

    newChatBtn && newChatBtn.addEventListener('click', ()=>{
      messages.innerHTML = '';
      userInput.value = '';
      userInput.focus();
    });
  }

  document.addEventListener('DOMContentLoaded', initPolishedChat);

})();
