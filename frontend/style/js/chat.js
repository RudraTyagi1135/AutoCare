// ======================================================
// AutoCare — Chat Page
// Polished Production Version
// ======================================================

(function () {

  function by(id) {
    return document.getElementById(id);
  }

  let isLoading = false;

  /* =========================
     SAFE HTML
  ========================= */
  function escapeHtml(unsafe) {
    return String(unsafe || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  /* =========================
     API CALL
  ========================= */
  async function callGeneralChat(question) {
    try {
      const res = await fetch("/api/chat/general", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: question
        })
      });

      if (!res.ok) {
        throw new Error("Server error");
      }

      const data = await res.json();

      return (
        data.reply ||
        "⚠️ No response received from the server."
      );

    } catch (err) {
      console.error("Chat API error:", err);

      return "⚠️ Chat service is temporarily unavailable. Please try again.";
    }
  }

  /* =========================
     MESSAGE UI
  ========================= */
  function addMessage(messagesEl, text, role = "assistant") {

    const el = document.createElement("div");

    el.className =
      "adv-msg " +
      (role === "user" ? "user" : "assistant");

    const body = document.createElement("div");

    body.innerHTML =
      escapeHtml(text).replace(/\n/g, "<br>");

    el.appendChild(body);

    messagesEl.appendChild(el);

    el.scrollIntoView({
      behavior: "smooth",
      block: "end"
    });
  }

  /* =========================
     THINKING UI
  ========================= */
  function createThinking(messagesEl) {

    const el = document.createElement("div");

    el.className = "adv-msg assistant";

    el.innerHTML = `
      <div>
        🤖 Analyzing your question...
      </div>
    `;

    messagesEl.appendChild(el);

    el.scrollIntoView({
      behavior: "smooth"
    });

    return el;
  }

  /* =========================
     WELCOME MESSAGE
  ========================= */
  function resetWelcome(messagesEl) {

    messagesEl.innerHTML = `
      <div class="adv-msg assistant">
        <div>
          👋 Welcome to AutoCare AI.

          <br><br>

          I can help you with:

          <br>• Diabetes risk analysis
          <br>• Heart disease risk analysis
          <br>• Stroke risk analysis
          <br>• Understanding prediction results
          <br>• General health questions

          <br><br>

          Ask a question below to get started.
        </div>
      </div>
    `;
  }

  /* =========================
     INIT CHAT
  ========================= */
  function initChat() {

    const input = by("polUserInput");
    const sendBtn = by("polSendBtn");
    const messages = by("polMessages");
    const chatList = by("polChatList");
    const newChatBtn = by("polNewChat");

    if (!messages || !input || !sendBtn) {
      return;
    }

    input.focus();

    /* -------------------------
       SEND MESSAGE
    ------------------------- */
    async function sendMessage() {

      if (isLoading) return;

      const text = input.value.trim();

      if (!text) return;

      isLoading = true;
      sendBtn.disabled = true;

      addMessage(messages, text, "user");

      input.value = "";

      const thinking = createThinking(messages);

      const answer =
        await callGeneralChat(text);

      thinking.remove();

      addMessage(
        messages,
        answer,
        "assistant"
      );

      /* -------------------------
         SAVE IN HISTORY
      ------------------------- */
      if (chatList) {

        const preview =
          text.length > 40
            ? text.substring(0, 40) + "..."
            : text;

        const item =
          document.createElement("div");

        item.className = "chat-item";

        item.dataset.q = text;

        item.innerHTML = `
          <div>
            🗨 ${escapeHtml(preview)}
          </div>
        `;

        chatList.prepend(item);
      }

      isLoading = false;
      sendBtn.disabled = false;

      input.focus();
    }

    /* -------------------------
       SEND EVENTS
    ------------------------- */
    sendBtn.addEventListener(
      "click",
      sendMessage
    );

    input.addEventListener(
      "keydown",
      (e) => {

        if (
          e.key === "Enter" &&
          !e.shiftKey
        ) {
          e.preventDefault();
          sendMessage();
        }

      }
    );

    /* -------------------------
       NEW CHAT
    ------------------------- */
    if (newChatBtn) {

      newChatBtn.addEventListener(
        "click",
        () => {

          resetWelcome(messages);

          input.value = "";

          input.focus();

        }
      );

    }

    /* -------------------------
       HISTORY CLICK
    ------------------------- */
    if (chatList) {

      chatList.addEventListener(
        "click",
        (e) => {

          const item =
            e.target.closest(".chat-item");

          if (!item) return;

          input.value =
            item.dataset.q || "";

          input.focus();

        }
      );

    }

    /* -------------------------
       INITIAL STATE
    ------------------------- */
    if (
      messages.children.length === 0
    ) {
      resetWelcome(messages);
    }

  }

  document.addEventListener(
    "DOMContentLoaded",
    initChat
  );

})();