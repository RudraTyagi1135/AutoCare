// ======================================================
// AutoCare — Advice Page (FINAL CLEAN VERSION)
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
     MESSAGE UI (CLEAN)
  ========================= */
  function addAdvMessage(messagesEl, text, role = 'assistant') {
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
  function createThinkingBubble(messagesEl, text = "Analyzing…") {
    const el = document.createElement('div');
    el.className = 'adv-msg assistant';
    el.innerHTML = `<div>${text}</div>`;

    messagesEl.appendChild(el);
    el.scrollIntoView({ behavior: 'smooth' });
    return el;
  }

  /* =========================
     API CALL
  ========================= */
  async function callMedicalChat(message) {
    try {
      const res = await fetch("/api/medical/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          prediction: window.predictionData || null
        })
      });

      if (!res.ok) throw new Error("Server error");

      const data = await res.json();

      if (!data.success) throw new Error(data.error);

      return data.reply;

    } catch (err) {
      console.error(err);
      return "⚠️ Something went wrong. Try again.";
    }
  }

  /* =========================
     INIT
  ========================= */
  function initAdvice() {

    const advMessages = by('advMessages');
    const advInput = by('advInput');
    const advSendBtn = by('advSendBtn');

    if (!advMessages || !advInput || !advSendBtn) return;

    advInput.focus();

    async function sendAdvice() {

      if (isLoading) return;

      const question = advInput.value.trim();
      if (!question) return;

      isLoading = true;

      addAdvMessage(advMessages, question, 'user');
      advInput.value = '';

      const thinking = createThinkingBubble(advMessages);

      const answer = await callMedicalChat(question);

      thinking.remove();
      addAdvMessage(advMessages, answer, 'assistant');

      isLoading = false;
    }

    advSendBtn.addEventListener('click', sendAdvice);

    advInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendAdvice();
      }
    });
  }

  document.addEventListener('DOMContentLoaded', initAdvice);

})();