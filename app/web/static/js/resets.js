const scopeEl = document.getElementById("scope");
const stateEl = document.getElementById("state");
const resultEl = document.getElementById("result");

if (window.LunetTheme && window.LunetI18n) {
  window.LunetTheme.initTheme();
  window.LunetI18n.initLang();
  window.LunetTheme.bindThemeToggle();
  window.LunetI18n.bindLangToggle();
  window.LunetI18n.bindStorageSync?.();
}

document.getElementById("resetBtn").addEventListener("click", async () => {
  stateEl.className = "status warn";
  stateEl.textContent = "Reset in progress...";
  try {
    const response = await fetch("/web/api/resets/traffic", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scope: scopeEl.value }),
    });
    if (response.status === 401) {
      window.location.href = "/web/login";
      return;
    }
    const data = await response.json();
    stateEl.className = "status ok";
    stateEl.textContent = "Reset completed";
    resultEl.textContent = JSON.stringify(data, null, 2);
  } catch {
    stateEl.className = "status err";
    stateEl.textContent = "Reset failed";
  }
});

document.querySelectorAll(".logout-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    await fetch("/web/logout", { method: "POST" });
    window.location.href = "/web/login";
  });
});
