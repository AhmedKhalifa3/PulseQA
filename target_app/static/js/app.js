// PulseChat Client Logic
let currentUser = null;
let currentToken = null;
let currentRoom = "general";
let socket = null;
let healthInterval = null;

const authScreen = document.getElementById("auth-screen");
const mainScreen = document.getElementById("main-screen");
const usernameInput = document.getElementById("username-input");
const passwordInput = document.getElementById("password-input");
const loginBtn = document.getElementById("login-button");
const logoutBtn = document.getElementById("logout-button");
const loginError = document.getElementById("login-error");
const channelList = document.getElementById("channel-list");
const activeChannelName = document.getElementById("active-channel-name");
const messagesList = document.getElementById("messages-list");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-button");
const messageCountBadge = document.getElementById("message-count-badge");
const metricCpu = document.getElementById("metric-cpu");
const metricRam = document.getElementById("metric-ram");
const stressToggleBtn = document.getElementById("stress-toggle-btn");
const stressDrawer = document.getElementById("stress-drawer");
const stressCpuBtn = document.getElementById("stress-cpu-btn");
const stressMemBtn = document.getElementById("stress-mem-btn");
const stressResetBtn = document.getElementById("stress-reset-btn");

// TTS Modal Elements
const ttsModal = document.getElementById("tts-modal");
const ttsOpenBtn = document.getElementById("tts-open-btn");
const ttsCloseBtn = document.getElementById("tts-close-btn");
const ttsTextInput = document.getElementById("tts-text-input");
const ttsLangSelect = document.getElementById("tts-lang-select");
const ttsGenerateBtn = document.getElementById("tts-generate-btn");

// Check for stored session
const storedToken = sessionStorage.getItem("pulse_token");
const storedUser = sessionStorage.getItem("pulse_user");
if (storedToken && storedUser) {
    currentUser = storedUser;
    currentToken = storedToken;
    showMainApp();
}

loginBtn.addEventListener("click", handleLogin);
passwordInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") handleLogin();
});

logoutBtn.addEventListener("click", handleLogout);
sendBtn.addEventListener("click", sendMessage);
messageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

// Stress drawer toggle
stressToggleBtn.addEventListener("click", () => {
    stressDrawer.style.display = stressDrawer.style.display === "none" ? "block" : "none";
});

stressCpuBtn.addEventListener("click", async () => {
    try {
        stressCpuBtn.disabled = true;
        stressCpuBtn.innerText = "Burning CPU...";
        await fetch("/api/system/stress/cpu", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ duration_sec: 1.5, intensity: 1.0 })
        });
    } catch (e) {
        console.error("Stress error:", e);
    } finally {
        stressCpuBtn.disabled = false;
        stressCpuBtn.innerText = "Burn CPU (1.5s)";
        pollHealth();
    }
});

stressMemBtn.addEventListener("click", async () => {
    try {
        await fetch("/api/system/stress/memory", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ memory_mb: 30 })
        });
        pollHealth();
    } catch (e) {
        console.error("Memory stress error:", e);
    }
});

stressResetBtn.addEventListener("click", async () => {
    try {
        await fetch("/api/system/stress/memory/reset", { method: "POST" });
        pollHealth();
    } catch (e) {
        console.error("Memory reset error:", e);
    }
});

// TTS modal handlers
ttsOpenBtn.addEventListener("click", () => {
    ttsTextInput.value = messageInput.value || "Hello from PulseChat audio engine.";
    ttsModal.style.display = "flex";
});

ttsCloseBtn.addEventListener("click", () => {
    ttsModal.style.display = "none";
});

ttsGenerateBtn.addEventListener("click", async () => {
    const text = ttsTextInput.value.trim();
    const lang = ttsLangSelect.value;
    if (!text) return;

    ttsGenerateBtn.disabled = true;
    ttsGenerateBtn.innerText = "Synthesizing...";

    try {
        const res = await fetch("/api/audio/synthesize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text, language: lang })
        });
        const data = await res.json();
        if (res.ok) {
            // Send synthesized audio message
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({
                    user: currentUser,
                    text: `[Audio Note: ${lang.toUpperCase()}] ${text}`,
                    audio: true,
                    audio_url: data.audio_base64
                }));
            }
            ttsModal.style.display = "none";
            ttsTextInput.value = "";
        } else {
            alert(data.detail || "TTS Synthesis failed");
        }
    } catch (e) {
        console.error("TTS error:", e);
    } finally {
        ttsGenerateBtn.disabled = false;
        ttsGenerateBtn.innerText = "Synthesize & Send";
    }
});

// Channel switching
channelList.querySelectorAll(".channel-item").forEach(item => {
    item.addEventListener("click", () => {
        const room = item.getAttribute("data-room");
        switchRoom(room);
    });
});

async function handleLogin() {
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    loginError.style.display = "none";

    try {
        const res = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (res.ok) {
            currentUser = data.username;
            currentToken = data.token;
            sessionStorage.setItem("pulse_token", currentToken);
            sessionStorage.setItem("pulse_user", currentUser);
            showMainApp();
        } else {
            loginError.innerText = data.detail || "Authentication failed";
            loginError.style.display = "block";
        }
    } catch (e) {
        loginError.innerText = "Connection error to server";
        loginError.style.display = "block";
    }
}

function handleLogout() {
    if (currentToken) {
        fetch("/api/auth/logout", {
            method: "POST",
            headers: { "Authorization": `Bearer ${currentToken}` }
        }).catch(() => {});
    }
    currentUser = null;
    currentToken = null;
    sessionStorage.clear();
    if (socket) socket.close();
    if (healthInterval) clearInterval(healthInterval);

    mainScreen.style.display = "none";
    authScreen.style.display = "flex";
    usernameInput.value = "";
    passwordInput.value = "";
}

function showMainApp() {
    authScreen.style.display = "none";
    mainScreen.style.display = "flex";
    document.getElementById("current-user-name").innerText = currentUser;
    document.getElementById("current-user-avatar").innerText = currentUser.substring(0, 2).toUpperCase();

    switchRoom("general");
    pollHealth();
    healthInterval = setInterval(pollHealth, 3000);
}

function switchRoom(room) {
    currentRoom = room;
    activeChannelName.innerText = room;

    channelList.querySelectorAll(".channel-item").forEach(item => {
        item.classList.toggle("active", item.getAttribute("data-room") === room);
    });

    if (socket) {
        socket.close();
    }
    initWebSocket(room);
    loadRoomMessages(room);
}

async function loadRoomMessages(room) {
    try {
        const res = await fetch(`/api/chat/messages/${room}`);
        const data = await res.json();
        messagesList.innerHTML = "";
        data.messages.forEach(renderMessage);
        messageCountBadge.innerText = `${data.messages.length} msgs`;
        scrollToBottom();
    } catch (e) {
        console.error("Failed to load messages", e);
    }
}

function initWebSocket(room) {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    socket = new WebSocket(`${protocol}//${window.location.host}/ws/${room}`);

    socket.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        renderMessage(msg);
        const count = messagesList.children.length;
        messageCountBadge.innerText = `${count} msgs`;
        scrollToBottom();
    };

    socket.onerror = (e) => {
        console.error("WebSocket error:", e);
    };
}

function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            user: currentUser,
            text: text,
            audio: false
        }));
        messageInput.value = "";
    }
}

function renderMessage(msg) {
    const isOutgoing = msg.user === currentUser;
    const msgEl = document.createElement("div");
    msgEl.className = `message-item ${isOutgoing ? "outgoing" : "incoming"}`;
    msgEl.setAttribute("data-testid", `message-item-${msg.id}`);

    let audioHtml = "";
    if (msg.audio && msg.audio_url) {
        audioHtml = `
            <div class="audio-player-box" data-testid="audio-player-${msg.id}">
                <audio controls src="${msg.audio_url}"></audio>
            </div>
        `;
    }

    msgEl.innerHTML = `
        <div class="message-meta">
            <span class="msg-sender" data-testid="msg-sender-${msg.id}">${escapeHtml(msg.user)}</span>
            <span class="msg-time">${msg.timestamp || ""}</span>
        </div>
        <div class="message-content" data-testid="message-text-${msg.id}">${escapeHtml(msg.text)}</div>
        ${audioHtml}
    `;

    messagesList.appendChild(msgEl);
}

function scrollToBottom() {
    const container = document.getElementById("messages-container");
    container.scrollTop = container.scrollHeight;
}

async function pollHealth() {
    try {
        const res = await fetch("/api/system/health");
        if (res.ok) {
            const data = await res.json();
            metricCpu.innerText = `${data.cpu_percent.toFixed(1)}%`;
            metricRam.innerText = `${data.memory_rss_mb.toFixed(1)} MB`;
        }
    } catch (e) {
        // silent fail on poll
    }
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
}
