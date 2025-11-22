// URL of your Flask backend
const API_BASE = "http://127.0.0.1:9000/api";

const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");

// Append a message bubble to the chat
function addMessageBubble(text, sender = "bot") {
  const row = document.createElement("div");
  row.classList.add("message-row", sender);

  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  bubble.textContent = text;

  row.appendChild(bubble);
  chatWindow.appendChild(row);

  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Call Flask backend
async function sendMessageToBot(message) {
  try {
    const response = await fetch(`${API_BASE}/chat/general`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return data.reply || "⚠️ No reply from server.";
  } catch (err) {
    console.error(err);
    return "⚠️ Error contacting chatbot backend.";
  }
}

// Handle form submit
chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;

  addMessageBubble(text, "user");
  userInput.value = "";
  userInput.focus();

  const typingId = `typing-${Date.now()}`;
  const typingRow = document.createElement("div");
  typingRow.classList.add("message-row", "bot");
  typingRow.id = typingId;

  const typingBubble = document.createElement("div");
  typingBubble.classList.add("bubble");
  typingBubble.textContent = "Thinking...";
  typingRow.appendChild(typingBubble);

  chatWindow.appendChild(typingRow);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  // Get reply from backend
  const reply = await sendMessageToBot(text);

  // Replace typing with final response
  const oldTyping = document.getElementById(typingId);
  if (oldTyping) {
    chatWindow.removeChild(oldTyping);
  }
  addMessageBubble(reply, "bot");
});

// Show welcome message on load
window.addEventListener("load", () => {
  addMessageBubble("Hi! I'm your AutoCare Assistant. How can I help you today?", "bot");
});
