// ======================================================
// AutoCare — Chat Page (FINAL CLEAN VERSION)
// Matches Advice UI + Sidebar History
// ======================================================

(function () {

  function by(id) { return document.getElementById(id); }

  let isLoading = false;

  /* =========================
     SAFE HTML
  ========================= */
  function escapeHtml(unsafe) {
    return String(unsafe || '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  /* =========================
     API CALL
  ========================= */
  async function callGeneralChat(question) {
    try {
      const res = await fetch("/api/chat/general", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question })
      });

      if (!res.ok) throw new Error("Server error");

      const data = await res.json();
      return data.reply || "⚠️ No response from server.";

    } catch (err) {
      console.error("Chat API error:", err);
      return "⚠️ Chat service unavailable. Try again.";
    }
  }

  /* =========================
     MESSAGE UI (MATCH ADVICE)
  ========================= */
  function addMessage(messagesEl, text, role = 'assistant') {
    const el = document.createElement('div');
    el.className = 'adv-msg ' + (role === 'user' ? 'user' : 'assistant');

    const body = document.createElement('div');
    body.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');

    el.appendChild(body);

    messagesEl.appendChild(el);
    el.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }

  /* =========================
     THINKING UI
  ========================= */
  function createThinking(messagesEl) {
    const el = document.createElement('div');
    el.className = 'adv-msg assistant';
    el.innerHTML = `<div>Thinking...</div>`;

    messagesEl.appendChild(el);
    el.scrollIntoView({ behavior: 'smooth' });
    return el;
  }

  /* =========================
     INIT
  ========================= */
  function initChat() {

    const input = by('polUserInput');
    const sendBtn = by('polSendBtn');
    const messages = by('polMessages');
    const chatList = by('polChatList');
    const newChatBtn = by('polNewChat');

    if (!messages || !input || !sendBtn) return;

    input.focus();

    /* -------------------------
       SEND MESSAGE
    ------------------------- */
    async function sendMessage() {

      if (isLoading) return;

      const text = input.value.trim();
      if (!text) return;

      isLoading = true;

      addMessage(messages, text, 'user');
      input.value = '';

      const thinking = createThinking(messages);

      const answer = await callGeneralChat(text);

      thinking.remove();
      addMessage(messages, answer, 'assistant');

      /* -------------------------
         SIDEBAR HISTORY
      ------------------------- */
      if (chatList) {
        const item = document.createElement('div');
        item.className = 'chat-item';
        item.dataset.q = text;
        item.innerHTML = `<div>${escapeHtml(text)}</div>`;
        chatList.prepend(item);
      }

      isLoading = false;
    }

    /* -------------------------
       EVENTS
    ------------------------- */
    sendBtn.addEventListener('click', sendMessage);

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    /* -------------------------
       NEW CHAT
    ------------------------- */
    if (newChatBtn) {
      newChatBtn.addEventListener('click', () => {
        messages.innerHTML = '';
        input.value = '';
        input.focus();
      });
    }

    /* -------------------------
       CLICK HISTORY → REUSE
    ------------------------- */
    if (chatList) {
      chatList.addEventListener('click', (e) => {
        const item = e.target.closest('.chat-item');
        if (item) {
          input.value = item.dataset.q || '';
          input.focus();
        }
      });
    }
  }

  document.addEventListener('DOMContentLoaded', initChat);

})();