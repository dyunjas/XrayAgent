const nickInput = document.getElementById("nick");
const passInput = document.getElementById("password");
const submitBtn = document.getElementById("submit");
const errBox = document.getElementById("err");
function t(key, fallback) {
  return window.LunetI18n?.t(key, fallback) || fallback || key;
}

async function login() {
  errBox.textContent = "";
  submitBtn.disabled = true;
  try {
    const response = await fetch("/web/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nick: nickInput.value.trim(),
        password: passInput.value,
      }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.detail || "Login failed");
    }
    window.location.href = "/web";
  } catch (error) {
    const msg = window.LunetUI.humanError(error.message, t("login.failed", "Login failed. Check username and password."));
    errBox.textContent = msg;
    window.LunetUI.showToast(msg, "err");
  } finally {
    submitBtn.disabled = false;
  }
}

submitBtn.addEventListener("click", login);
nickInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") login();
});
passInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") login();
});

window.LunetTheme.initTheme();
window.LunetI18n.initLang();
window.LunetTheme.bindThemeToggle();
window.LunetI18n.bindLangToggle();
window.LunetI18n.bindStorageSync?.();
