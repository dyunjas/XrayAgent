const rowsEl = document.getElementById("rows");
const statsEl = document.getElementById("statsState");
const nickLabelEl = document.getElementById("nickLabel");
const moodChipEl = document.getElementById("moodChip");
const createMsgEl = document.getElementById("createMsg");
const userIdInputEl = document.getElementById("newUserId");
const levelInputEl = document.getElementById("newLevel");
const createBtnEl = document.getElementById("createKeyBtn");
const genUserIdBtnEl = document.getElementById("genUserIdBtn");
const createdUriValueEl = document.getElementById("createdUriValue");
const copyCreatedUriBtnEl = document.getElementById("copyCreatedUriBtn");
const onlineUsersEl = document.getElementById("onlineUsers");
const topUsersEl = document.getElementById("topUsers");
const onlineSupportStateEl = document.getElementById("onlineSupportState");
const searchEl = document.getElementById("clientsSearch");
const sortEl = document.getElementById("clientsSort");
const filterEl = document.getElementById("clientsFilter");
const sideDbBadgeEl = document.getElementById("sideDbBadge");
const sideStatsBadgeEl = document.getElementById("sideStatsBadge");

let allUsers = [];

function t(key, fallback) {
  return window.LunetI18n?.t(key, fallback) || fallback || key;
}

function fmtBytes(input) {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let value = Number(input || 0);
  let idx = 0;
  while (value >= 1024 && idx < units.length - 1) {
    value /= 1024;
    idx += 1;
  }
  return `${value.toFixed(idx > 0 ? 2 : 0)} ${units[idx]}`;
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

async function copyToClipboard(value) {
  if (!value || value === "-") return;
  try {
    await navigator.clipboard.writeText(value);
    window.LunetUI.showToast(t("dashboard.uri_copied", "URI copied to clipboard"), "ok");
  } catch {
    window.LunetUI.showToast(t("dashboard.uri_copy_failed", "Cannot copy URI in this browser context"), "warn");
  }
}

function normalizedUserText(user) {
  return `${user.user_id} ${user.email || ""} ${user.uuid || ""}`.toLowerCase();
}

function applyClientsView(users) {
  const prefs = window.LunetUI.getPrefs();
  const query = (searchEl.value || "").trim().toLowerCase();
  const filter = filterEl.value || prefs.clients_default_filter || "all";
  const sort = sortEl.value || prefs.clients_default_sort || "online_desc";

  let list = users.slice();
  if (query) {
    list = list.filter((u) => normalizedUserText(u).includes(query));
  }
  if (filter === "online") list = list.filter((u) => u.online);
  if (filter === "offline") list = list.filter((u) => !u.online);

  list.sort((a, b) => {
    if (sort === "traffic_desc") return b.total - a.total;
    if (sort === "traffic_asc") return a.total - b.total;
    if (sort === "id_asc") return a.user_id - b.user_id;
    if (sort === "id_desc") return b.user_id - a.user_id;
    if (a.online !== b.online) return a.online ? -1 : 1;
    return b.total - a.total;
  });

  const pageSize = Math.max(10, Math.min(1000, Number(prefs.clients_page_size || 100)));
  return list.slice(0, pageSize);
}

function renderUsers(users) {
  rowsEl.innerHTML = "";
  for (const user of users) {
    const onlineClass = user.online ? "online" : "";
    const onlineText = user.online_supported
      ? (user.online ? t("common.online", "online") : t("common.offline", "offline"))
      : t("common.unknown", "unknown");
    const uriShort = user.uri || "-";
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="status-pill ${onlineClass}">${onlineText}</span></td>
      <td>${user.user_id}</td>
      <td>${user.email}</td>
      <td>${fmtBytes(user.total)}</td>
      <td>
        <div class="uri-cell">
          <span class="uri-text" title="${uriShort}">${uriShort}</span>
          <button class="copy-btn" data-uri="${uriShort}">${t("dashboard.copy", "Copy")}</button>
        </div>
      </td>
    `;
    rowsEl.appendChild(tr);
  }

  rowsEl.querySelectorAll(".copy-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      await copyToClipboard(btn.getAttribute("data-uri"));
    });
  });
}

function renderOnline(users) {
  const onlineOnly = users.filter((u) => u.online);
  if (!onlineOnly.length) {
    onlineUsersEl.innerHTML = `<div class="online-traffic">${t("dashboard.no_users_online", "No users online now")}</div>`;
    return;
  }
  onlineUsersEl.innerHTML = onlineOnly.map((u) => `
    <div class="online-item">
      <span class="dot online"></span>
      <div>
        <div class="online-user">${u.email}</div>
        <div class="online-traffic">${t("dashboard.id_label", "ID")} ${u.user_id}</div>
      </div>
      <div class="online-traffic">${fmtBytes(u.total)}</div>
    </div>
  `).join("");
}

function renderTopUsers(topUsers) {
  if (!topUsers || !topUsers.length) {
    topUsersEl.innerHTML = `<div class="online-traffic">${t("dashboard.no_traffic_data", "No traffic data yet")}</div>`;
    return;
  }
  topUsersEl.innerHTML = topUsers.map((u) => `
    <div class="top-user">
      <div class="u">${u.email}</div>
      <div class="t">${fmtBytes(u.total)} ${t("dashboard.total_suffix", "total")}</div>
    </div>
  `).join("");
}

function renderClients() {
  const filtered = applyClientsView(allUsers);
  renderUsers(filtered);
}

function suggestNextUserId() {
  const maxId = allUsers.reduce((acc, item) => Math.max(acc, Number(item.user_id || 0)), 1000);
  const nextId = maxId + 1;
  userIdInputEl.value = String(nextId);
  return nextId;
}

async function loadSideStatus() {
  try {
    const response = await fetch("/web/api/xray/settings");
    if (response.status === 401) return;
    const data = await response.json();
    sideDbBadgeEl.textContent = data.db_ok ? t("sidebar.db_ok", "DB: OK") : t("sidebar.db_err", "DB: ERR");
    sideStatsBadgeEl.textContent = data.stats_available ? t("sidebar.stats_on", "Stats: ON") : t("sidebar.stats_off", "Stats: OFF");
  } catch {
    sideDbBadgeEl.textContent = t("sidebar.db_unknown", "DB: ?");
    sideStatsBadgeEl.textContent = t("sidebar.stats_unknown", "Stats: ?");
  }
}

async function loadDashboard() {
  const response = await fetch("/web/api/dashboard");
  if (response.status === 401) {
    window.location.href = "/web/login";
    return;
  }
  const data = await response.json();

  nickLabelEl.textContent = `${t("common.user", "User")}: ${data.nick}`;
  setText("active", String(data.summary.active_keys));
  setText("onlineNow", String(data.summary.online_now));
  setText("inbound", fmtBytes(data.summary.inbound_total));
  setText("usersTotal", fmtBytes(data.summary.users_total));
  setText("cpu", `${(data.server.cpu_percent || 0).toFixed(1)}%`);
  setText("mem", `${(data.server.mem_percent || 0).toFixed(1)}%`);
  setText("onlineRatio", `${(data.summary.online_ratio_percent || 0).toFixed(1)}%`);
  setText("avgUserTraffic", fmtBytes(data.summary.avg_user_total || 0));

  statsEl.textContent = data.stats_available ? t("common.online", "online") : t("common.offline", "offline");
  onlineSupportStateEl.textContent = `${t("dashboard.online_metrics", "online metrics")}: ${data.summary.online_supported_users}/${data.summary.active_keys}`;

  allUsers = data.users || [];
  if (!userIdInputEl.value) {
    suggestNextUserId();
  }
  renderClients();
  renderOnline(allUsers);
  renderTopUsers(data.top_users || []);
}

function showCreateMessage(text, mode) {
  createMsgEl.className = "status";
  if (mode) createMsgEl.classList.add(mode);
  createMsgEl.textContent = text;
}

async function createKey() {
  const userId = Number(userIdInputEl.value);
  const level = Number(levelInputEl.value || 0);
  if (!Number.isInteger(userId) || userId <= 0) {
    showCreateMessage(t("dashboard.create_invalid_user_id", "Enter valid user_id > 0"), "err");
    return;
  }
  if (!Number.isInteger(level) || level < 0 || level > 255) {
    showCreateMessage(t("dashboard.create_invalid_level", "Level must be 0..255"), "err");
    return;
  }

  createBtnEl.disabled = true;
  showCreateMessage(t("dashboard.create_in_progress", "Creating Xray user and URI..."), "warn");
  try {
    const response = await fetch("/web/api/keys", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, level }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Failed to create key");

    if (data.uri) {
      const prefs = window.LunetUI.getPrefs();
      createdUriValueEl.value = data.uri;
      if (prefs.auto_copy_uri) {
        await copyToClipboard(data.uri);
      }
      showCreateMessage(`${t("dashboard.create_success", "Client created")}: ${data.uuid}`, "ok");
    } else {
      showCreateMessage(t("dashboard.create_empty_uri", "Client created, but URI is empty. Set XRAY_PUBLIC_* in .env"), "warn");
    }
    await loadDashboard();
  } catch (error) {
    const msg = window.LunetUI.humanError(error.message, t("dashboard.create_failed", "Could not create client key."));
    showCreateMessage(msg, "err");
    window.LunetUI.showToast(msg, "err");
  } finally {
    createBtnEl.disabled = false;
  }
}

async function runQuickAction(path, successKey, successFallback) {
  showCreateMessage(t("common.processing", "Processing action..."), "warn");
  try {
    const response = await fetch(path, { method: "POST" });
    if (response.status === 401) {
      window.location.href = "/web/login";
      return;
    }
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Action failed");
    const successText = t(successKey, successFallback);
    showCreateMessage(successText, "ok");
    window.LunetUI.showToast(successText, "ok");
    await loadDashboard();
  } catch (error) {
    const msg = window.LunetUI.humanError(error.message, t("dashboard.action_failed", "Action failed. Check Xray and DB."));
    showCreateMessage(msg, "err");
    window.LunetUI.showToast(msg, "err");
  }
}

async function logout() {
  await fetch("/web/logout", { method: "POST" });
  window.location.href = "/web/login";
}

function rerenderLanguageSensitive() {
  nickLabelEl.textContent = `${t("common.user", "User")}: ${nickLabelEl.textContent.split(":").slice(1).join(":").trim() || "-"}`;
  renderClients();
  renderOnline(allUsers);
  const currentTop = (allUsers || []).slice().sort((a, b) => (b.total || 0) - (a.total || 0)).slice(0, 5);
  renderTopUsers(currentTop);
}

searchEl.addEventListener("input", renderClients);
sortEl.addEventListener("change", renderClients);
filterEl.addEventListener("change", renderClients);
createBtnEl.addEventListener("click", createKey);
genUserIdBtnEl.addEventListener("click", () => {
  const next = suggestNextUserId();
  window.LunetUI.showToast(`${t("dashboard.suggested_id", "Suggested user ID")}: ${next}`, "info");
});
copyCreatedUriBtnEl.addEventListener("click", async () => {
  await copyToClipboard(createdUriValueEl.value);
});
document.getElementById("resyncBtn").addEventListener("click", async () => {
  await runQuickAction("/web/api/dashboard/resync", "dashboard.resync_completed", "Resync completed");
});
document.getElementById("resetUsersBtn").addEventListener("click", async () => {
  await runQuickAction("/web/api/dashboard/reset_users_traffic", "dashboard.reset_completed", "Users traffic reset completed");
});
const sideLogoutEl = document.getElementById("sideLogout");
if (sideLogoutEl) sideLogoutEl.addEventListener("click", logout);
document.querySelectorAll(".logout-btn").forEach((btn) => {
  btn.addEventListener("click", logout);
});
document.addEventListener("lunet:lang-changed", async () => {
  rerenderLanguageSensitive();
  await loadSideStatus();
  await loadDashboard();
});

window.LunetTheme.initTheme();
window.LunetI18n.initLang();
window.LunetTheme.bindThemeToggle();
window.LunetI18n.bindLangToggle();
window.LunetI18n.bindStorageSync?.();
const prefs = window.LunetUI.applyPrefs();
if (sortEl && prefs.clients_default_sort) sortEl.value = prefs.clients_default_sort;
if (filterEl && prefs.clients_default_filter) filterEl.value = prefs.clients_default_filter;
loadSideStatus();
loadDashboard();
const refreshSec = Number(prefs.dashboard_refresh_sec || 15);
setInterval(loadDashboard, Math.min(120, Math.max(5, refreshSec)) * 1000);
setInterval(loadSideStatus, 20000);
