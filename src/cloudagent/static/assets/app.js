const $ = (selector) => document.querySelector(selector);
const state = { busy: false, session: localStorage.getItem("cloudagent-session") || `demo-${Math.random().toString(36).slice(2, 8)}` };

function setSession() { localStorage.setItem("cloudagent-session", state.session); $("#session").textContent = state.session; }
function addMessage(role, text, handoff = false) {
  const row = document.createElement("div");
  row.className = `message ${role}`;
  row.innerHTML = `<span class="avatar">${role === "assistant" ? "C" : "你"}</span><div><b>${role === "assistant" ? "CloudAgent" : "你"}</b><p></p>${handoff ? '<small class="handoff">↗ 建议转人工处理</small>' : ""}</div>`;
  row.querySelector("p").textContent = text;
  $("#messages").appendChild(row);
  $("#messages").scrollTop = $("#messages").scrollHeight;
}
function renderEvidence(data) {
  const host = $("#evidence");
  host.innerHTML = "";
  $("#evidence-count").textContent = `${data.evidence.length} ITEMS`;
  data.evidence.forEach((item) => {
    const card = document.createElement("article");
    card.className = "evidence-card";
    card.innerHTML = `<div><b></b><span></span></div><p></p><code></code>`;
    card.querySelector("b").textContent = item.title;
    card.querySelector("span").textContent = `${Math.round(item.score * 100)}% match`;
    card.querySelector("p").textContent = item.snippet;
    card.querySelector("code").textContent = item.id;
    host.appendChild(card);
  });
  data.trace.forEach((step) => {
    const line = document.createElement("div");
    line.className = "trace-line";
    line.textContent = `${step.name} · ${step.detail}`;
    host.appendChild(line);
  });
}
async function send(value) {
  const message = value.trim();
  if (!message || state.busy) return;
  state.busy = true; $("#message").value = ""; $("#thinking").hidden = false; addMessage("user", message);
  try {
    const response = await fetch("/v1/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message, session_id: state.session }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "请求失败");
    addMessage("assistant", data.answer, data.handoff); renderEvidence(data);
  } catch (error) { addMessage("assistant", `这次请求没有完成：${error.message}`, true); }
  finally { $("#thinking").hidden = true; state.busy = false; }
}
async function newSession() {
  if (state.busy) return;
  await fetch(`/v1/sessions/${encodeURIComponent(state.session)}/reset`, { method: "POST" }).catch(() => {});
  state.session = `demo-${Math.random().toString(36).slice(2, 8)}`; setSession(); $("#messages").innerHTML = '<div class="welcome"><b>新会话已准备好。</b><span>请描述需要帮助的问题。</span></div>'; $("#evidence").innerHTML = '<p class="empty">发送问题后，这里会显示证据与决策轨迹。</p>'; $("#evidence-count").textContent = "0 ITEMS";
}
$("#chat-form").addEventListener("submit", (event) => { event.preventDefault(); send($("#message").value); });
$("#message").addEventListener("keydown", (event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); send(event.target.value); } });
$("#message").addEventListener("input", (event) => { event.target.style.height = "auto"; event.target.style.height = `${Math.min(event.target.scrollHeight, 110)}px`; });
$("#new-session").addEventListener("click", newSession); setSession();
