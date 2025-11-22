// ---------------- BASE URL --------------------
const API_BASE = "http://127.0.0.1:9000/api/medical";

// DOM elements
const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");

// Add message bubble
function addBubble(text, sender="bot") {
  const row = document.createElement("div");
  row.classList.add("message-row", sender);

  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  bubble.textContent = text;

  row.appendChild(bubble);
  chatWindow.appendChild(row);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ---------------- API CALL -------------------
async function callMedicalChat(message) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });
  return res.json();
}

// ---------------- EVENT LISTENER -------------
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;

  addBubble(text, "user");
  userInput.value = "";

  const thinking = document.createElement("div");
  thinking.classList.add("message-row", "bot");
  thinking.textContent = "Thinking...";
  chatWindow.appendChild(thinking);

  const response = await callMedicalChat(text);

  chatWindow.removeChild(thinking);

  if (response.success) {
    addBubble(response.reply, "bot");
  } else {
    addBubble("⚠️ Error: " + response.error, "bot");
  }
});

// ---------------- WELCOME MESSAGE -------------
window.addEventListener("load", () => {
  addBubble("Hi! I'm your AutoCare Medical Assistant. How can I help you today?", "bot");
});
