// static/script.js

const API_BASE = "http://localhost:8000/api";
let currentFileId = null;

// Initialize page
document.addEventListener("DOMContentLoaded", () => {
  loadFiles();
  loadStats();
  setupEventListeners();
});

function setupEventListeners() {
  // File upload
  const uploadArea = document.getElementById("uploadArea");
  const fileInput = document.getElementById("fileInput");

  uploadArea.addEventListener("click", () => fileInput.click());
  uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = "#667eea";
  });
  uploadArea.addEventListener("dragleave", () => {
    uploadArea.style.borderColor = "rgba(255,255,255,0.3)";
  });
  uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file);
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files[0]) handleFileUpload(e.target.files[0]);
  });

  // Upload button
  document.getElementById("uploadBtn").addEventListener("click", () => {
    if (fileInput.files[0]) handleFileUpload(fileInput.files[0]);
  });

  // Send message
  document.getElementById("sendBtn").addEventListener("click", sendMessage);
  document.getElementById("messageInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // File filter
  document.getElementById("fileFilter").addEventListener("change", (e) => {
    const fileSelect = document.getElementById("fileSelect");
    fileSelect.disabled = !e.target.checked;
    currentFileId = e.target.checked ? fileSelect.value : null;
  });

  document.getElementById("fileSelect").addEventListener("change", (e) => {
    currentFileId = e.target.value;
  });
}

async function handleFileUpload(file) {
  const strategy = document.getElementById("chunkStrategy").value;
  const statusDiv = document.getElementById("uploadStatus");

  statusDiv.innerHTML = '<div class="loading"></div> Processing...';

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${API_BASE}/upload?strategy=${strategy}`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (response.ok) {
      statusDiv.innerHTML = `<div class="success-message">✅ ${data.message}</div>`;
      loadFiles();
      loadStats();
      addMessage(
        "bot",
        `File "${file.name}" uploaded successfully! ${data.chunk_count} chunks. You can now ask questions.`,
      );
    } else {
      statusDiv.innerHTML = `<div class="error-message">❌ ${data.detail}</div>`;
    }
  } catch (error) {
    statusDiv.innerHTML = `<div class="error-message">❌ Connection error: ${error.message}</div>`;
  }
}

async function loadFiles() {
  try {
    const response = await fetch(`${API_BASE}/files`);
    const data = await response.json();

    const filesList = document.getElementById("filesList");
    const fileSelect = document.getElementById("fileSelect");

    if (data.files.length === 0) {
      filesList.innerHTML =
        '<p class="empty-message">No files uploaded yet</p>';
      fileSelect.innerHTML = '<option value="">All files</option>';
      fileSelect.disabled = true;
      return;
    }

    filesList.innerHTML = "";
    fileSelect.innerHTML = '<option value="">All files</option>';

    data.files.forEach((file) => {
      // Add to sidebar list
      const fileDiv = document.createElement("div");
      fileDiv.className = "file-item";
      fileDiv.innerHTML = `
                <span class="file-name">📄 ${file.name}</span>
                <span class="delete-file" onclick="deleteFile('${file.id}')">🗑️</span>
            `;
      filesList.appendChild(fileDiv);

      // Add to dropdown list
      const option = document.createElement("option");
      option.value = file.id;
      option.textContent = `${file.name} (${file.chunks} chunks)`;
      fileSelect.appendChild(option);
    });

    fileSelect.disabled = false;
  } catch (error) {
    console.error("Error loading files:", error);
  }
}

async function deleteFile(fileId) {
  if (!confirm("Are you sure you want to delete this file?")) return;

  try {
    const response = await fetch(`${API_BASE}/delete/${fileId}`, {
      method: "DELETE",
    });

    if (response.ok) {
      loadFiles();
      loadStats();
      addMessage("bot", "🗑️ File deleted from the system.");
    }
  } catch (error) {
    console.error("Error deleting file:", error);
  }
}

async function loadStats() {
  try {
    const response = await fetch(`${API_BASE}/stats`);
    const data = await response.json();

    const statsDiv = document.getElementById("stats");
    statsDiv.innerHTML = `
            <p>📊 Total chunks: ${data.vector_store.total_chunks}</p>
            <p>📁 Active files: ${data.active_files}</p>
        `;

    // Update model info
    const health = await fetch(`${API_BASE}/health`);
    const healthData = await health.json();
    document.getElementById("modelBadge").innerHTML =
      `🧠 ${healthData.llm_model.split("/").pop()}`;
  } catch (error) {
    console.error("Error loading stats:", error);
  }
}

async function sendMessage() {
  const input = document.getElementById("messageInput");
  const query = input.value.trim();

  if (!query) return;

  // Display user question
  addMessage("user", query);
  input.value = "";

  // Loading indicator
  addLoadingIndicator();

  try {
    const response = await fetch(`${API_BASE}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        file_id: currentFileId,
        top_k: 3,
      }),
    });

    removeLoadingIndicator();

    const data = await response.json();

    if (response.ok) {
      let answerHtml = `<p>${data.answer}</p>`;

      if (data.sources && data.sources.length > 0) {
        answerHtml += `<div class="sources">
                    <strong>📚 Sources:</strong><br>
                    ${data.sources.map((s, i) => `[${i + 1}] ${s.content.substring(0, 150)}...`).join("<br>")}
                </div>`;
        answerHtml += `<small>⏱️ Processing time: ${data.processing_time.toFixed(2)} seconds</small>`;
      }

      addMessage("bot", answerHtml);
    } else {
      addMessage("bot", `❌ Error: ${data.detail}`);
    }
  } catch (error) {
    removeLoadingIndicator();
    addMessage("bot", `❌ Connection error: ${error.message}`);
  }
}

function addMessage(role, content) {
  const messagesDiv = document.getElementById("chatMessages");
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${role}`;

  const avatar = role === "user" ? "👤" : "🤖";
  const avatarClass = role === "user" ? "message-avatar" : "message-avatar";

  messageDiv.innerHTML = `
        <div class="${avatarClass}">${avatar}</div>
        <div class="message-content">${content}</div>
    `;

  messagesDiv.appendChild(messageDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addLoadingIndicator() {
  const messagesDiv = document.getElementById("chatMessages");
  const loadingDiv = document.createElement("div");
  loadingDiv.className = "message bot";
  loadingDiv.id = "loadingIndicator";
  loadingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content"><div class="loading"></div> Thinking...</div>
    `;
  messagesDiv.appendChild(loadingDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function removeLoadingIndicator() {
  const indicator = document.getElementById("loadingIndicator");
  if (indicator) indicator.remove();
}

// SQL Bonus modal
function openSqlModal() {
  const modal = document.getElementById("sqlModal");
  modal.style.display = "flex";

  document.querySelector(".close").onclick = () => {
    modal.style.display = "none";
  };

  document.getElementById("executeSqlBtn").onclick = async () => {
    const sqlQuery = document.getElementById("sqlQuery").value;
    if (!sqlQuery) {
      alert("Please enter a SQL query");
      return;
    }

    const resultDiv = document.getElementById("sqlResult");
    resultDiv.innerHTML = '<div class="loading"></div> Executing...';

    try {
      const response = await fetch(`${API_BASE}/query-sql`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: sqlQuery,
          server: localStorage.getItem("sql_server") || "localhost",
          database: localStorage.getItem("sql_database") || "",
          username: "",
          password: "",
        }),
      });

      const data = await response.json();

      if (response.ok) {
        resultDiv.innerHTML = `
                    <div class="success-message">
                        ✅ ${data.message}<br>
                        📊 Rows: ${data.rows}<br>
                        📋 Columns: ${data.columns.join(", ")}<br>
                        📄 Chunks: ${data.chunks}
                    </div>
                    <pre>${JSON.stringify(data.sample_data, null, 2)}</pre>
                `;
        loadStats();
      } else {
        resultDiv.innerHTML = `<div class="error-message">❌ ${data.detail}</div>`;
      }
    } catch (error) {
      resultDiv.innerHTML = `<div class="error-message">❌ ${error.message}</div>`;
    }
  };
}

// Add SQL button to the interface (optional)
const sqlButton = document.createElement("button");
sqlButton.className = "btn btn-secondary";
sqlButton.innerHTML = "🗄️ SQL Server (Bonus)";
sqlButton.style.marginTop = "10px";
sqlButton.onclick = openSqlModal;
document.querySelector(".upload-section").appendChild(sqlButton);
