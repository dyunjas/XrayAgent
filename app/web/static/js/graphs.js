const serverCanvas = document.getElementById("serverChart");
const serverCtx = serverCanvas.getContext("2d");
const xrayCanvas = document.getElementById("xrayChart");
const xrayCtx = xrayCanvas.getContext("2d");
const stateEl = document.getElementById("graphState");

const serverPoints = [];
const xrayPoints = [];
let lastSample = null;

function t(key, fallback) {
  return window.LunetI18n?.t(key, fallback) || fallback || key;
}

function getGraphPrefs() {
  const prefs = window.LunetUI.getPrefs();
  return {
    refreshSec: Math.min(30, Math.max(2, Number(prefs.graphs_refresh_sec || 5))),
    lineWidth: Math.min(6, Math.max(2, Number(prefs.graphs_line_width || 3))),
    maxPoints: Math.min(180, Math.max(30, Number(prefs.graphs_points || 90))),
  };
}

function pushPoint(arr, sample, maxPoints) {
  arr.push(sample);
  if (arr.length > maxPoints) arr.shift();
}

function drawGrid(ctx, canvas) {
  const css = getComputedStyle(document.documentElement);
  const bg = (css.getPropertyValue("--panel-2") || "#0f1d33").trim();
  const line = (css.getPropertyValue("--line") || "#2a3b56").trim();
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = line;
  ctx.lineWidth = 1;
  for (let i = 1; i <= 5; i += 1) {
    const y = (canvas.height / 6) * i;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }
}

function drawLine(ctx, canvas, values, color, maxValue, lineWidth) {
  if (!values.length) return;
  ctx.beginPath();
  ctx.strokeStyle = color;
  ctx.lineWidth = lineWidth;
  ctx.shadowColor = color;
  ctx.shadowBlur = 6;
  values.forEach((v, i) => {
    const x = (i / (values.length - 1 || 1)) * canvas.width;
    const y = canvas.height - (v / (maxValue || 1)) * canvas.height;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.shadowBlur = 0;
}

function drawServerChart(lineWidth) {
  drawGrid(serverCtx, serverCanvas);
  const cpu = serverPoints.map((p) => p.cpu_percent || 0);
  const mem = serverPoints.map((p) => p.mem_percent || 0);
  drawLine(serverCtx, serverCanvas, cpu, "#f3c16a", 100, lineWidth);
  drawLine(serverCtx, serverCanvas, mem, "#f58fc2", 100, lineWidth);
}

function drawXrayChart(lineWidth) {
  drawGrid(xrayCtx, xrayCanvas);
  const inbound = xrayPoints.map((p) => p.inbound_total || 0);
  const users = xrayPoints.map((p) => p.users_total || 0);
  const keys = xrayPoints.map((p) => p.active_keys || 0);
  const online = xrayPoints.map((p) => p.online_now || 0);
  const trafficMax = Math.max(...inbound, ...users, 1);
  const usersMax = Math.max(...keys, ...online, 1);
  drawLine(xrayCtx, xrayCanvas, inbound, "#3ac9ff", trafficMax, lineWidth);
  drawLine(xrayCtx, xrayCanvas, users, "#38d39f", trafficMax, lineWidth);
  drawLine(xrayCtx, xrayCanvas, keys, "#8aa4ff", usersMax, lineWidth);
  drawLine(xrayCtx, xrayCanvas, online, "#53e0bf", usersMax, lineWidth);
}

function renderCharts() {
  const prefs = getGraphPrefs();
  drawServerChart(prefs.lineWidth);
  drawXrayChart(prefs.lineWidth);
}

function renderLiveState(sample) {
  if (!sample) return;
  const pattern = t("graphs.live_status", "Live • Keys {keys} • Online {online} • CPU {cpu}%");
  stateEl.className = "status ok";
  stateEl.textContent = pattern
    .replace("{keys}", String(sample.active_keys ?? 0))
    .replace("{online}", String(sample.online_now ?? 0))
    .replace("{cpu}", Number(sample.cpu_percent || 0).toFixed(1));
}

async function poll() {
  try {
    const response = await fetch("/web/api/graphs/live");
    if (response.status === 401) {
      window.location.href = "/web/login";
      return;
    }
    const data = await response.json();
    const prefs = getGraphPrefs();
    pushPoint(serverPoints, data, prefs.maxPoints);
    pushPoint(xrayPoints, data, prefs.maxPoints);
    renderCharts();

    lastSample = data;
    renderLiveState(data);
  } catch (error) {
    stateEl.className = "status err";
    const msg = window.LunetUI.humanError(error?.message, t("graphs.live_unavailable", "Live data is unavailable now."));
    stateEl.textContent = msg;
    window.LunetUI.showToast(msg, "err");
  }
}

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
  if (lastSample) renderLiveState(lastSample);
});
poll();
setInterval(poll, getGraphPrefs().refreshSec * 1000);
