// js/advice.js
// Advice page → connects to MEDICAL chatbot: /api/medical/chat

(function(){
  function by(id){ return document.getElementById(id); }

  function addAdvMessage(messagesEl, text, role='assistant'){
    const el = document.createElement('div');
    el.className = 'adv-msg ' + (role === 'user' ? 'user' : 'assistant');

    const meta = document.createElement('div');
    meta.className = 'meta';
    meta.textContent = role === 'user' ? 'You' : 'Assistant';

    const body = document.createElement('div');
    body.innerHTML = String(text).replace(/\n/g,'<br>');

    
    el.appendChild(meta);
    el.appendChild(body);

    messagesEl.appendChild(el);
    el.scrollIntoView({ behavior:'smooth', block:'end' });
  }

  // REAL API → medical chatbot
  async function callMedicalChat(message){
    try {
      const res = await fetch("/api/medical/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message })
      });

      return await res.json();
    } catch (e){
      return { success: false, reply: "⚠️ Backend error." };
    }
  }

  async function initPolishedAdvice(){
    const advMessages = by('advMessages');
    const advInput = by('advInput');
    const advSendBtn = by('advSendBtn');
    const history = by('advHistory');

    if(!advMessages || !advInput) return;

    advInput.focus();

    advSendBtn.addEventListener('click', async ()=>{
      const question = advInput.value.trim();
      if(!question) return;

      addAdvMessage(advMessages, question, 'user');
      advInput.value = '';

      // Loading bubble
      const thinking = document.createElement('div');
      thinking.className = 'adv-msg assistant';
      thinking.innerHTML = '<div class="meta">Assistant</div><div>Thinking...</div>';
      advMessages.appendChild(thinking);
      thinking.scrollIntoView({behavior:'smooth'});

      // CALL MEDICAL CHAT API
      const response = await callMedicalChat(question);

      thinking.remove();

      if(response.success){
        addAdvMessage(advMessages, response.reply, 'assistant');
      } else {
        addAdvMessage(advMessages, "⚠️ Error: " + response.error, 'assistant');
      }

      // save history item
      if(history){
        const item = document.createElement('div');
        item.className = 'adv-item';
        item.setAttribute('data-q', question);
        item.innerHTML = `<div class="icon">•</div><div class="title">${question}</div>`;
        history.prepend(item);
      }
    });

    advInput.addEventListener('keydown', (e)=>{
      if(e.key === 'Enter' && !e.shiftKey){
        e.preventDefault();
        advSendBtn.click();
      }
    });

    // history click
    history && history.addEventListener('click', (e)=>{
      const item = e.target.closest('.adv-item');
      if(item){
        advInput.value = item.getAttribute('data-q');
      }
    });
  }

  document.addEventListener('DOMContentLoaded', initPolishedAdvice);
})();
