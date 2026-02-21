const coreDataEl = document.getElementById("coreData");
const depsDataEl = document.getElementById("depsData");
const dbDataEl = document.getElementById("dbData");
const resyncStateEl = document.getElementById("resyncState");
const configStateEl = document.getElementById("configState");
const configPathEl = document.getElementById("configPath");
const configEditorEl = document.getElementById("configEditor");
const apiRowsEl = document.getElementById("apiRows");
const apiSearchEl = document.getElementById("apiSearch");
const dbBadgeEl = document.getElementById("dbBadge");
const statsBadgeEl = document.getElementById("statsBadge");
const inboundsBadgeEl = document.getElementById("inboundsBadge");
const outboundsBadgeEl = document.getElementById("outboundsBadge");
const publicKeyValueEl = document.getElementById("publicKeyValue");
const privateKeyValueEl = document.getElementById("privateKeyValue");
const shortIdValueEl = document.getElementById("shortIdValue");

let cachedSettings = null;
let cachedEndpoints = [];

function tr(key, fallback) {
  if (window.LunetI18n && typeof window.LunetI18n.t === "function") {
    return window.LunetI18n.t(key, fallback);
  }
  return fallback || key;
}

function kvRow(key, value) {
  return `<div class="kv-row"><span class="k">${key}</span><span class="v">${value}</span></div>`;
}

function setState(el, text, cls) {
  el.className = "status";
  if (cls) el.classList.add(cls);
  el.textContent = text;
}

async function copyValue(text) {
  if (!text || text === "-") return;
  try {
    await navigator.clipboard.writeText(text);
    window.LunetUI.showToast(tr("dashboard.uri_copied", "URI copied to clipboard"), "ok");
  } catch {
    window.LunetUI.showToast(tr("dashboard.uri_copy_failed", "Cannot copy URI in this browser context"), "warn");
  }
}

function renderApiRows() {
  const q = (apiSearchEl.value || "").trim().toLowerCase();
  const endpoints = cachedEndpoints.filter((e) => {
    if (!q) return true;
    return `${e.method} ${e.path} ${e.auth} ${e.description}`.toLowerCase().includes(q);
  });
  apiRowsEl.innerHTML = endpoints.map((e) => `
    <tr>
      <td>${e.method}</td>
      <td><code>${e.path}</code></td>
      <td>${e.auth}</td>
      <td>${e.description}</td>
    </tr>
  `).join("");
}

function renderSettings(data) {
  cachedSettings = data;
  const summary = data.config_summary || {};
  const keys = data.xray_keys || {};

  dbBadgeEl.textContent = data.db_ok ? tr("panel.connected", "Connected") : tr("panel.error", "Error");
  statsBadgeEl.textContent = data.stats_available ? tr("panel.enabled", "Enabled") : tr("panel.disabled", "Disabled");
  inboundsBadgeEl.textContent = String(summary.inbounds_count ?? 0);
  outboundsBadgeEl.textContent = String(summary.outbounds_count ?? 0);

  publicKeyValueEl.value = keys.public_key || "-";
  privateKeyValueEl.value = keys.private_key || "-";
  shortIdValueEl.value = keys.short_id || "-";

  coreDataEl.innerHTML =
    kvRow(tr("xray.k_xray_addr", "Xray address"), data.xray_addr) +
    kvRow(tr("xray.k_inbound_tag", "Inbound tag"), data.inbound_tag) +
    kvRow(tr("xray.k_sync_server_id", "Sync server id"), data.sync_server_id) +
    kvRow(tr("xray.k_config_path", "Config path"), data.config_path) +
    kvRow(tr("xray.k_routing_rules", "Routing rules"), summary.routing_rules_count ?? 0) +
    kvRow(tr("xray.k_api_enabled", "API enabled"), String(summary.api_enabled ?? false)) +
    kvRow(tr("xray.k_log_level", "Log level"), summary.loglevel || "-") +
    kvRow(tr("xray.k_config_error", "Config error"), data.config_error || "-");

  const depsMissing = (data.dependencies_missing || []).length ? data.dependencies_missing.join(", ") : tr("xray.missing_none", "none");
  depsDataEl.innerHTML =
    kvRow("grpcurl", data.grpcurl_bin) +
    kvRow("protoc", data.protoc_bin) +
    kvRow("protoset", data.protoset) +
    kvRow(tr("xray.k_missing", "Missing"), depsMissing) +
    kvRow(tr("xray.k_stats_available", "Stats available"), String(data.stats_available));

  dbDataEl.innerHTML =
    kvRow(tr("panel.connected", "Connected"), String(data.db_ok)) +
    kvRow(tr("panel.error", "Error"), data.db_error || "-");

  cachedEndpoints = data.api_endpoints || [];
  renderApiRows();
}

async function loadSettings() {
  const response = await fetch("/web/api/xray/settings");
  if (response.status === 401) {
    window.location.href = "/web/login";
    return;
  }
  if (!response.ok) {
    throw new Error(`settings status ${response.status}`);
  }
  const data = await response.json();
  renderSettings(data);
}

async function loadConfig() {
  const response = await fetch("/web/api/xray/config");
  if (response.status === 401) {
    window.location.href = "/web/login";
    return;
  }
  const d = await response.json();
  configPathEl.textContent = d.path || "-";
  if (d.error) setState(configStateEl, window.LunetUI.humanError(d.error, tr("xray.read_config_failed", "Cannot read xray config file.")), "err");
  configEditorEl.value = JSON.stringify(d.config || {}, null, 2);
}

document.getElementById("copyPublicKeyBtn").addEventListener("click", async () => {
  await copyValue(publicKeyValueEl.value);
});
document.getElementById("copyPrivateKeyBtn").addEventListener("click", async () => {
  await copyValue(privateKeyValueEl.value);
});
document.getElementById("copyShortIdBtn").addEventListener("click", async () => {
  await copyValue(shortIdValueEl.value);
});

document.getElementById("formatConfigBtn").addEventListener("click", () => {
  try {
    const parsed = JSON.parse(configEditorEl.value || "{}");
    configEditorEl.value = JSON.stringify(parsed, null, 2);
    setState(configStateEl, tr("xray.json_formatted", "JSON formatted"), "ok");
  } catch {
    setState(configStateEl, tr("xray.invalid_json", "Invalid JSON format."), "err");
  }
});

document.getElementById("validateConfigBtn").addEventListener("click", () => {
  try {
    JSON.parse(configEditorEl.value || "{}");
    setState(configStateEl, tr("xray.json_valid", "JSON is valid"), "ok");
  } catch {
    setState(configStateEl, tr("xray.json_invalid", "JSON is invalid"), "err");
  }
});

document.getElementById("saveConfigBtn").addEventListener("click", async () => {
  setState(configStateEl, tr("xray.saving", "Saving config..."), "warn");
  let parsed;
  try {
    parsed = JSON.parse(configEditorEl.value || "{}");
  } catch {
    setState(configStateEl, tr("xray.invalid_json", "Invalid JSON format."), "err");
    return;
  }
  try {
    const response = await fetch("/web/api/xray/config", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ config: parsed }),
    });
    if (response.status === 401) {
      window.location.href = "/web/login";
      return;
    }
    const d = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(d.detail || "Save failed");
    setState(configStateEl, tr("xray.config_saved", "Config saved"), "ok");
    window.LunetUI.showToast(tr("xray.saved_ok", "Xray config saved successfully"), "ok");
    await loadSettings();
  } catch (e) {
    const msg = window.LunetUI.humanError(e.message, tr("xray.save_failed", "Cannot save xray config."));
    setState(configStateEl, msg, "err");
    window.LunetUI.showToast(msg, "err");
  }
});

document.getElementById("restartBtn").addEventListener("click", async () => {
  setState(configStateEl, tr("xray.restarting", "Restarting xray..."), "warn");
  try {
    const response = await fetch("/web/api/xray/restart", { method: "POST" });
    if (response.status === 401) {
      window.location.href = "/web/login";
      return;
    }
    const d = await response.json();
    if (!d.ok) throw new Error(d.detail || d.stderr || "Restart failed");
    setState(configStateEl, tr("xray.restart_ok", "Xray restarted"), "ok");
    window.LunetUI.showToast(tr("xray.restart_ok", "Xray restarted"), "ok");
  } catch (e) {
    const msg = window.LunetUI.humanError(e.message, tr("xray.restart_failed", "Cannot restart xray."));
    setState(configStateEl, msg, "err");
    window.LunetUI.showToast(msg, "err");
  }
});

document.getElementById("resyncBtn").addEventListener("click", async () => {
  setState(resyncStateEl, tr("xray.resync_progress", "Resync in progress..."), "warn");
  try {
    const response = await fetch("/web/api/xray/resync", { method: "POST" });
    if (response.status === 401) {
      window.location.href = "/web/login";
      return;
    }
    const data = await response.json();
    const msg = tr("xray.resync_done", "Resync done: synced {synced}, failed {failed}")
      .replace("{synced}", String(data.synced || 0))
      .replace("{failed}", String((data.failed || []).length));
    setState(resyncStateEl, msg, "ok");
    window.LunetUI.showToast(msg, "ok");
  } catch (e) {
    const msg = window.LunetUI.humanError(e.message, tr("xray.resync_failed", "Resync failed. Check DB and Xray connection."));
    setState(resyncStateEl, msg, "err");
    window.LunetUI.showToast(msg, "err");
  }
});

apiSearchEl.addEventListener("input", renderApiRows);

document.querySelectorAll(".logout-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    await fetch("/web/logout", { method: "POST" });
    window.location.href = "/web/login";
  });
});

window.LunetTheme.initTheme();
window.LunetI18n.initLang();
window.LunetTheme.bindThemeToggle();
window.LunetI18n.bindLangToggle();
window.LunetI18n.bindStorageSync?.();

document.addEventListener("lunet:lang-changed", () => {
  if (cachedSettings) renderSettings(cachedSettings);
  renderApiRows();
});

loadSettings();
loadConfig();
setInterval(loadSettings, 20000);
