const saveBtnEl = document.getElementById("saveAllBtn");
const saveStateEl = document.getElementById("saveState");
const statusRowsEl = document.getElementById("statusRows");
const securityWarningEl = document.getElementById("securityWarning");

const dashboardRefreshEl = document.getElementById("dashboardRefreshSec");
const autoCopyUriEl = document.getElementById("autoCopyUri");
const graphsRefreshEl = document.getElementById("graphsRefreshSec");
const graphsLineWidthEl = document.getElementById("graphsLineWidth");
const graphsPointsEl = document.getElementById("graphsPoints");
const compactModeEl = document.getElementById("compactMode");
const showToastsEl = document.getElementById("showToasts");
const clientsDefaultSortEl = document.getElementById("clientsDefaultSort");
const clientsDefaultFilterEl = document.getElementById("clientsDefaultFilter");
const clientsPageSizeEl = document.getElementById("clientsPageSize");

const cpuGaugeEl = document.getElementById("cpuGauge");
const memGaugeEl = document.getElementById("memGauge");
const onlineGaugeEl = document.getElementById("onlineGauge");
const cpuGaugeTextEl = document.getElementById("cpuGaugeText");
const memGaugeTextEl = document.getElementById("memGaugeText");
const onlineGaugeTextEl = document.getElementById("onlineGaugeText");

function t(key, fallback) {
  return window.LunetI18n?.t(key, fallback) || fallback || key;
}

function setState(text, cls) {
  saveStateEl.className = "status";
  if (cls) saveStateEl.classList.add(cls);
  saveStateEl.textContent = text;
}

function setGauge(el, textEl, value) {
  const v = Math.max(0, Math.min(100, Number(value) || 0));
  el.style.setProperty("--p", String(v));
  textEl.textContent = `${v.toFixed(1)}%`;
}

function loadPrefs() {
  const p = window.LunetUI.getPrefs();
  dashboardRefreshEl.value = p.dashboard_refresh_sec;
  autoCopyUriEl.checked = !!p.auto_copy_uri;
  graphsRefreshEl.value = p.graphs_refresh_sec;
  graphsLineWidthEl.value = p.graphs_line_width;
  graphsPointsEl.value = p.graphs_points;
  compactModeEl.checked = !!p.compact_mode;
  showToastsEl.checked = !!p.show_toasts;
  clientsDefaultSortEl.value = p.clients_default_sort || "online_desc";
  clientsDefaultFilterEl.value = p.clients_default_filter || "all";
  clientsPageSizeEl.value = p.clients_page_size || 100;
}

function normalizeInt(value, min, max, fallback) {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  return Math.min(max, Math.max(min, Math.round(n)));
}

function renderStatus(settings, dashboard) {
  statusRowsEl.innerHTML = `
    <div class="status-row">
      <span class="status-name">${t("panel.database", "Database")}</span>
      <span class="status-value ${settings.db_ok ? "ok" : "err"}">${settings.db_ok ? t("panel.connected", "Connected") : t("panel.error", "Error")}</span>
    </div>
    <div class="status-row">
      <span class="status-name">${t("panel.xray_stats_api", "Xray Stats API")}</span>
      <span class="status-value ${settings.stats_available ? "ok" : "err"}">${settings.stats_available ? t("panel.enabled", "Enabled") : t("panel.disabled", "Disabled")}</span>
    </div>
    <div class="status-row">
      <span class="status-name">${t("panel.active_keys", "Active Keys")}</span>
      <span class="status-value">${dashboard.summary?.active_keys ?? 0}</span>
    </div>
    <div class="status-row">
      <span class="status-name">${t("panel.online_users", "Online Users")}</span>
      <span class="status-value">${dashboard.summary?.online_now ?? 0}</span>
    </div>
  `;

  setGauge(cpuGaugeEl, cpuGaugeTextEl, dashboard.server?.cpu_percent || 0);
  setGauge(memGaugeEl, memGaugeTextEl, dashboard.server?.mem_percent || 0);
  setGauge(onlineGaugeEl, onlineGaugeTextEl, dashboard.summary?.online_ratio_percent || 0);
}

async function loadStatuses() {
  try {
    let sRes = await fetch("/web/api/panel/settings");
    if (sRes.status === 404) {
      sRes = await fetch("/web/api/xray/settings");
    }
    const dRes = await fetch("/web/api/dashboard");

    if (sRes.status === 401 || dRes.status === 401) {
      window.location.href = "/web/login";
      return;
    }
    if (!sRes.ok || !dRes.ok) {
      throw new Error("status fetch failed");
    }

    const [settings, dashboard] = await Promise.all([sRes.json(), dRes.json()]);
    renderStatus(settings, dashboard);
  } catch (error) {
    window.LunetUI.showToast(window.LunetUI.humanError(error?.message, t("panel.status_load_failed", "Cannot load panel status")), "err");
  }
}

saveBtnEl.addEventListener("click", () => {
  const next = {
    dashboard_refresh_sec: normalizeInt(dashboardRefreshEl.value, 5, 120, 15),
    auto_copy_uri: !!autoCopyUriEl.checked,
    graphs_refresh_sec: normalizeInt(graphsRefreshEl.value, 2, 30, 5),
    graphs_line_width: normalizeInt(graphsLineWidthEl.value, 2, 6, 3),
    graphs_points: normalizeInt(graphsPointsEl.value, 30, 180, 90),
    compact_mode: !!compactModeEl.checked,
    show_toasts: !!showToastsEl.checked,
    clients_default_sort: clientsDefaultSortEl.value || "online_desc",
    clients_default_filter: clientsDefaultFilterEl.value || "all",
    clients_page_size: normalizeInt(clientsPageSizeEl.value, 10, 1000, 100),
  };

  window.LunetUI.setPrefs(next);
  window.LunetUI.applyPrefs();
  setState(t("panel.saved_hint", "Settings saved. Reload dashboard/graphs to fully apply intervals."), "ok");
  window.LunetUI.showToast(t("panel.saved_ok", "Panel settings saved"), "ok");
});

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
window.LunetUI.applyPrefs();
loadPrefs();
loadStatuses();
document.addEventListener("lunet:lang-changed", () => {
  loadStatuses();
});

if (location.protocol !== "https:") {
  securityWarningEl.hidden = false;
}
