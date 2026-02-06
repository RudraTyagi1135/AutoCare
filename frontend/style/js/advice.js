// js/advice.js
// Advice page → connects to MEDICAL chatbot: /api/medical/chat

(function () {
  function by(id) { return document.getElementById(id); }

  function escapeHtml(unsafe) {
    return String(unsafe || '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function addAdvMessage(messagesEl, text, role = 'assistant') {
    const el = document.createElement('div');
    el.className = 'adv-msg ' + (role === 'user' ? 'user' : 'assistant');

    const meta = document.createElement('div');
    meta.className = 'meta';
    meta.textContent = role === 'user' ? 'You' : 'Assistant';

    const body = document.createElement('div');
    body.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');

    el.appendChild(meta);
    el.appendChild(body);

    messagesEl.appendChild(el);
    el.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }

  // =========================
  // BACKEND CALL (SAFE)
  // =========================
  async function callMedicalChat(message) {
    try {
      const res = await fetch("/api/medical/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });

      if (!res.ok) {
        throw new Error("Server error: " + res.status);
      }

      const data = await res.json();

      if (!data.success) {
        throw new Error(data.error || "Medical chat failed");
      }

      return data.reply;

    } catch (err) {
      console.error("Medical chat error:", err);
      return "⚠️ Medical assistant is temporarily unavailable. Please try again.";
    }
  }

  // =========================
  // INIT
  // =========================
  async function initPolishedAdvice() {
    const advMessages = by('advMessages');
    const advInput = by('advInput');
    const advSendBtn = by('advSendBtn');
    const history = by('advHistory');

    if (!advMessages || !advInput || !advSendBtn) return;
    advInput.focus();

    async function sendAdvice() {
      const question = advInput.value.trim();
      if (!question) return;

      addAdvMessage(advMessages, question, 'user');
      advInput.value = '';

      // Thinking bubble
      const thinking = document.createElement('div');
      thinking.className = 'adv-msg assistant';
      thinking.innerHTML = `<div class="meta">Assistant</div><div>Thinking…</div>`;
      advMessages.appendChild(thinking);
      thinking.scrollIntoView({ behavior: 'smooth' });

      const answer = await callMedicalChat(question);

      thinking.remove();
      addAdvMessage(advMessages, answer, 'assistant');

      // Save to history
      if (history) {
        const item = document.createElement('div');
        item.className = 'adv-item';
        item.dataset.q = question;
        item.innerHTML = `
          <div class="icon">•</div>
          <div class="title">${escapeHtml(question)}</div>
        `;
        history.prepend(item);
      }
    }

    advSendBtn.addEventListener('click', sendAdvice);

    advInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendAdvice();
      }
    });

    // Click history → reuse question
    history && history.addEventListener('click', (e) => {
      const item = e.target.closest('.adv-item');
      if (item) {
        advInput.value = item.dataset.q || '';
        advInput.focus();
      }
    });
  }

  document.addEventListener('DOMContentLoaded', initPolishedAdvice);
})();
