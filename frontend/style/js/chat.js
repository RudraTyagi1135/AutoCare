// js/chat.js
// Chat page → connects to GENERAL chatbot: /api/chat/general

(function () {
  function by(id) { return document.getElementById(id); }

  function timeNow() {
    const d = new Date();
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function escapeHtml(unsafe) {
    return String(unsafe || '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  // =========================
  // BACKEND CALL (SAFE)
  // =========================
  async function callGeneralChat(question) {
    try {
      const res = await fetch("/api/chat/general", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question })
      });

      if (!res.ok) {
        throw new Error("Server error: " + res.status);
      }

      const data = await res.json();
      return data.reply || "⚠️ No reply field from server.";

    } catch (err) {
      console.error("Chat API error:", err);
      return "⚠️ Chat service unavailable. Please try again.";
    }
  }

  // =========================
  // UI HELPERS
  // =========================
  function addMessage(messagesEl, text, role = 'assistant') {
    const el = document.createElement('div');
    el.className = 'msg ' + (role === 'user' ? 'user' : 'assistant');

    const meta = document.createElement('div');
    meta.className = 'meta';
    meta.textContent = role === 'user' ? 'You' : 'Assistant';

    const body = document.createElement('div');
    body.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');

    const tm = document.createElement('div');
    tm.className = 'time';
    tm.textContent = timeNow();

    el.appendChild(meta);
    el.appendChild(body);
    el.appendChild(tm);

    messagesEl.appendChild(el);
    el.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }

  // =========================
  // MAIN INIT
  // =========================
  async function initPolishedChat() {
    const userInput = by('polUserInput');
    const sendBtn = by('polSendBtn');
    const messages = by('polMessages');
    const chatList = by('polChatList');
    const newChatBtn = by('polNewChat');

    if (!messages || !userInput || !sendBtn) return;
    userInput.focus();

    async function sendMessage() {
      const text = (userInput.value || '').trim();
      if (!text) return;

      addMessage(messages, text, 'user');
      userInput.value = '';

      // Typing placeholder
      const placeholder = document.createElement('div');
      placeholder.className = 'msg assistant';
      placeholder.innerHTML =
        `<div class="meta">Assistant</div>
         <div>Thinking <span class="typing"><span></span><span></span><span></span></span></div>
         <div class="time">--</div>`;
      messages.appendChild(placeholder);
      placeholder.scrollIntoView({ behavior: 'smooth', block: 'end' });

      // API CALL
      const answer = await callGeneralChat(text);

      placeholder.remove();
      addMessage(messages, answer, 'assistant');

      // Sidebar history
      if (chatList) {
        const item = document.createElement('div');
        item.className = 'chat-item';
        item.dataset.q = text;
        item.innerHTML =
          `<div class="icon"></div>
           <div class="title">${escapeHtml(text)}</div>`;
        chatList.prepend(item);
      }
    }

    sendBtn.addEventListener('click', (e) => {
      e.preventDefault();
      sendMessage();
    });

    userInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    newChatBtn && newChatBtn.addEventListener('click', () => {
      messages.innerHTML = '';
      userInput.value = '';
      userInput.focus();
    });
  }

  document.addEventListener('DOMContentLoaded', initPolishedChat);
})();
