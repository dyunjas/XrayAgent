(function () {
  const THEME_KEY = "lunet_theme";
  const LANG_KEY = "lunet_lang";
  const PREFS_KEY = "lunet_prefs";
  const DEFAULT_PREFS = {
    dashboard_refresh_sec: 15,
    graphs_refresh_sec: 5,
    graphs_line_width: 3,
    graphs_points: 90,
    auto_copy_uri: true,
    compact_mode: false,
    show_toasts: true,
    clients_default_sort: "online_desc",
    clients_default_filter: "all",
    clients_page_size: 100,
  };

  const TRANSLATIONS = {
    en: {
      "common.theme_light": "Light theme",
      "common.theme_dark": "Dark theme",
      "common.user": "User",
      "common.online": "online",
      "common.offline": "offline",
      "common.unknown": "unknown",
      "common.processing": "Processing action...",
      "common.operation_failed": "Operation failed. Try again.",
      "common.session_expired": "Session expired. Please login again.",
      "common.already_exists": "This user already has an active key.",
      "common.connection_error": "Cannot reach backend/Xray service.",
      "common.permission_denied": "Permission denied for this action.",
      "common.input_invalid": "Input is invalid. Please check the fields.",
      "sidebar.overview": "Overview",
      "sidebar.management": "Management",
      "sidebar.home": "Home",
      "sidebar.xray_settings": "Xray Settings",
      "sidebar.graphs": "Graphs",
      "sidebar.session": "Session",
      "sidebar.panel_settings": "Panel Settings",
      "sidebar.logout": "Logout",
      "sidebar.db_ok": "DB: OK",
      "sidebar.db_err": "DB: ERR",
      "sidebar.db_unknown": "DB: ?",
      "sidebar.stats_on": "Stats: ON",
      "sidebar.stats_off": "Stats: OFF",
      "sidebar.stats_unknown": "Stats: ?",
      "dashboard.breadcrumbs": "Home | Lunet Panel Dashboard",
      "dashboard.title": "Lunet Usage",
      "dashboard.subtitle": "Connected users, traffic and quick controls",
      "dashboard.resync": "Resync",
      "dashboard.reset_users": "Reset Users",
      "dashboard.online_now": "Online now",
      "dashboard.active_keys": "Active keys",
      "dashboard.average_cpu": "Average CPU",
      "dashboard.ram_usage": "RAM usage",
      "dashboard.online_ratio": "Online ratio",
      "dashboard.avg_user_traffic": "Avg/user traffic",
      "dashboard.inbound_total": "Inbound total",
      "dashboard.users_total": "Users total",
      "dashboard.xray_stats": "Xray stats",
      "dashboard.online_users": "Online Users",
      "dashboard.online_metrics": "online metrics",
      "dashboard.no_users_online": "No users online now",
      "dashboard.create_key_uri": "Create Key + URI",
      "dashboard.ready": "ready",
      "dashboard.suggest_id": "Suggest ID",
      "dashboard.created_uri": "Last created URI",
      "dashboard.suggested_id": "Suggested user ID",
      "dashboard.user_id": "User ID",
      "dashboard.level": "Level",
      "dashboard.create": "Create",
      "dashboard.top_users_by_traffic": "Top users by traffic",
      "dashboard.no_traffic_data": "No traffic data yet",
      "dashboard.search_placeholder": "Search by id, email, uuid...",
      "dashboard.sort_online_first": "Online first",
      "dashboard.sort_traffic_desc": "Traffic: high to low",
      "dashboard.sort_traffic_asc": "Traffic: low to high",
      "dashboard.sort_id_asc": "User ID: ascending",
      "dashboard.sort_id_desc": "User ID: descending",
      "dashboard.filter_all": "All clients",
      "dashboard.filter_online": "Online only",
      "dashboard.filter_offline": "Offline only",
      "dashboard.table_status": "Status",
      "dashboard.table_user": "User",
      "dashboard.table_email": "Email",
      "dashboard.table_traffic": "Traffic",
      "dashboard.table_uri": "URI",
      "dashboard.copy": "Copy",
      "dashboard.uri_copied": "URI copied to clipboard",
      "dashboard.uri_copy_failed": "Cannot copy URI in this browser context",
      "dashboard.id_label": "ID",
      "dashboard.total_suffix": "total",
      "dashboard.create_invalid_user_id": "Enter valid user_id > 0",
      "dashboard.create_invalid_level": "Level must be 0..255",
      "dashboard.create_in_progress": "Creating Xray user and URI...",
      "dashboard.create_success": "Client created",
      "dashboard.create_empty_uri": "Client created, but URI is empty. Set XRAY_PUBLIC_* in .env",
      "dashboard.create_failed": "Could not create client key.",
      "dashboard.action_failed": "Action failed. Check Xray and DB.",
      "dashboard.resync_completed": "Resync completed",
      "dashboard.reset_completed": "Users traffic reset completed",
      "panel.breadcrumbs": "Home | Panel Settings",
      "panel.title": "Panel Settings",
      "panel.subtitle": "Appearance, refresh, client table and graph behavior",
      "panel.security_title": "Security Warning",
      "panel.security_text": "Connection is not encrypted. Use HTTPS before entering sensitive data.",
      "panel.cpu": "CPU",
      "panel.memory": "Memory",
      "panel.online_ratio": "Online Ratio",
      "panel.appearance": "Appearance",
      "panel.theme_mode": "Theme mode",
      "panel.switch_theme": "Switch Theme",
      "panel.compact_mode": "Compact mode",
      "panel.show_notifications": "Show notifications",
      "panel.dashboard": "Dashboard",
      "panel.refresh_period": "Refresh period (sec)",
      "panel.auto_copy_uri": "Auto-copy URI after create",
      "panel.clients_rows_limit": "Clients rows limit",
      "panel.default_sort": "Default sort",
      "panel.default_filter": "Default filter",
      "panel.graphs": "Graphs",
      "panel.polling_interval": "Polling interval (sec)",
      "panel.line_width": "Line width (2-6)",
      "panel.history_points": "History points (30-180)",
      "panel.save_all": "Save all settings",
      "panel.service_status": "Service Status",
      "panel.database": "Database",
      "panel.xray_stats_api": "Xray Stats API",
      "panel.active_keys": "Active Keys",
      "panel.online_users": "Online Users",
      "panel.connected": "Connected",
      "panel.error": "Error",
      "panel.enabled": "Enabled",
      "panel.disabled": "Disabled",
      "panel.saved_ok": "Panel settings saved",
      "panel.saved_hint": "Settings saved. Reload dashboard/graphs to fully apply intervals.",
      "panel.status_load_failed": "Cannot load panel status",
      "graphs.breadcrumbs": "Home | Graphs",
      "graphs.title": "Live Graphs",
      "graphs.subtitle": "Server and Xray metrics on separate charts",
      "graphs.server_metrics": "Server Metrics",
      "graphs.xray_metrics": "Xray Metrics",
      "graphs.cpu_percent": "CPU %",
      "graphs.memory_percent": "Memory %",
      "graphs.inbound_traffic": "Inbound traffic",
      "graphs.users_traffic": "Users traffic",
      "graphs.active_keys": "Active keys",
      "graphs.online_users": "Online users",
      "graphs.live_status": "Live • Keys {keys} • Online {online} • CPU {cpu}%",
      "graphs.live_unavailable": "Live data is unavailable now.",
      "login.title": "Welcome to Lunet Panel",
      "login.subtitle": "Sign in to manage Xray",
      "login.username": "Username",
      "login.password": "Password",
      "login.submit": "Login",
      "login.failed": "Login failed. Check username and password.",
      "xray.title": "Xray Configuration",
      "xray.breadcrumbs": "Home | Xray Settings",
      "xray.subtitle": "Readable status, editable config and developer API list",
      "xray.save": "Save Config",
      "xray.restart": "Restart Xray",
      "xray.resync": "Resync",
      "xray.runtime": "Runtime Summary",
      "xray.dependencies": "Dependencies",
      "xray.database": "Database",
      "xray.config": "Xray config.json",
      "xray.api": "Developer API (Xray Management)",
      "xray.search_api": "Search endpoints...",
      "xray.format_json": "Format JSON",
      "xray.validate": "Validate",
      "xray.keys_title": "Key Materials",
      "xray.public_key": "Public key",
      "xray.private_key": "Private key",
      "xray.short_id": "Short ID",
      "xray.copy": "Copy",
      "xray.db_short": "DB",
      "xray.stats_api_short": "Stats API",
      "xray.inbounds_short": "Inbounds",
      "xray.outbounds_short": "Outbounds",
      "xray.method": "Method",
      "xray.path": "Path",
      "xray.auth": "Auth",
      "xray.description": "Description",
      "xray.k_xray_addr": "Xray address",
      "xray.k_inbound_tag": "Inbound tag",
      "xray.k_sync_server_id": "Sync server id",
      "xray.k_config_path": "Config path",
      "xray.k_routing_rules": "Routing rules",
      "xray.k_api_enabled": "API enabled",
      "xray.k_log_level": "Log level",
      "xray.k_config_error": "Config error",
      "xray.k_missing": "Missing",
      "xray.k_stats_available": "Stats available",
      "xray.missing_none": "none",
      "xray.read_config_failed": "Cannot read xray config file.",
      "xray.json_formatted": "JSON formatted",
      "xray.invalid_json": "Invalid JSON format.",
      "xray.json_valid": "JSON is valid",
      "xray.json_invalid": "JSON is invalid",
      "xray.saving": "Saving config...",
      "xray.config_saved": "Config saved",
      "xray.save_failed": "Cannot save xray config.",
      "xray.restarting": "Restarting xray...",
      "xray.restart_failed": "Cannot restart xray.",
      "xray.resync_progress": "Resync in progress...",
      "xray.resync_done": "Resync done: synced {synced}, failed {failed}",
      "xray.saved_ok": "Xray config saved successfully",
      "xray.restart_ok": "Xray restarted",
      "xray.resync_failed": "Resync failed. Check DB and Xray connection.",
    },
    ru: {
      "common.theme_light": "Светлая тема",
      "common.theme_dark": "Темная тема",
      "common.user": "Пользователь",
      "common.online": "онлайн",
      "common.offline": "оффлайн",
      "common.unknown": "неизвестно",
      "common.processing": "Выполняется действие...",
      "common.operation_failed": "Операция не выполнена. Попробуйте снова.",
      "common.session_expired": "Сессия истекла. Войдите снова.",
      "common.already_exists": "У этого пользователя уже есть активный ключ.",
      "common.connection_error": "Нет соединения с backend/Xray сервисом.",
      "common.permission_denied": "Недостаточно прав для этого действия.",
      "common.input_invalid": "Некорректные данные. Проверьте поля.",
      "sidebar.overview": "Обзор",
      "sidebar.management": "Управление",
      "sidebar.home": "Главная",
      "sidebar.xray_settings": "Настройки Xray",
      "sidebar.graphs": "Графики",
      "sidebar.session": "Сессия",
      "sidebar.panel_settings": "Настройки панели",
      "sidebar.logout": "Выход",
      "sidebar.db_ok": "БД: OK",
      "sidebar.db_err": "БД: ERR",
      "sidebar.db_unknown": "БД: ?",
      "sidebar.stats_on": "Стат: ON",
      "sidebar.stats_off": "Стат: OFF",
      "sidebar.stats_unknown": "Стат: ?",
      "dashboard.breadcrumbs": "Главная | Панель Lunet",
      "dashboard.title": "Сводка Lunet",
      "dashboard.subtitle": "Подключенные пользователи, трафик и быстрые действия",
      "dashboard.resync": "Ресинк",
      "dashboard.reset_users": "Сброс трафика",
      "dashboard.online_now": "Сейчас онлайн",
      "dashboard.active_keys": "Активные ключи",
      "dashboard.average_cpu": "Средний CPU",
      "dashboard.ram_usage": "Использование RAM",
      "dashboard.online_ratio": "Доля онлайн",
      "dashboard.avg_user_traffic": "Трафик на пользователя",
      "dashboard.inbound_total": "Входящий трафик",
      "dashboard.users_total": "Трафик пользователей",
      "dashboard.xray_stats": "Статус Xray",
      "dashboard.online_users": "Пользователи онлайн",
      "dashboard.online_metrics": "онлайн-метрики",
      "dashboard.no_users_online": "Сейчас нет пользователей онлайн",
      "dashboard.create_key_uri": "Создание ключа + URI",
      "dashboard.ready": "готово",
      "dashboard.suggest_id": "Подобрать ID",
      "dashboard.created_uri": "Последний созданный URI",
      "dashboard.suggested_id": "Рекомендуемый user ID",
      "dashboard.user_id": "User ID",
      "dashboard.level": "Уровень",
      "dashboard.create": "Создать",
      "dashboard.top_users_by_traffic": "Топ пользователей по трафику",
      "dashboard.no_traffic_data": "Данные по трафику пока отсутствуют",
      "dashboard.search_placeholder": "Поиск по id, email, uuid...",
      "dashboard.sort_online_first": "Сначала онлайн",
      "dashboard.sort_traffic_desc": "Трафик: по убыванию",
      "dashboard.sort_traffic_asc": "Трафик: по возрастанию",
      "dashboard.sort_id_asc": "User ID: по возрастанию",
      "dashboard.sort_id_desc": "User ID: по убыванию",
      "dashboard.filter_all": "Все клиенты",
      "dashboard.filter_online": "Только онлайн",
      "dashboard.filter_offline": "Только оффлайн",
      "dashboard.table_status": "Статус",
      "dashboard.table_user": "Пользователь",
      "dashboard.table_email": "Email",
      "dashboard.table_traffic": "Трафик",
      "dashboard.table_uri": "URI",
      "dashboard.copy": "Копировать",
      "dashboard.uri_copied": "URI скопирован в буфер",
      "dashboard.uri_copy_failed": "Не удалось скопировать URI в этом контексте браузера",
      "dashboard.id_label": "ID",
      "dashboard.total_suffix": "всего",
      "dashboard.create_invalid_user_id": "Введите корректный user_id > 0",
      "dashboard.create_invalid_level": "Уровень должен быть в диапазоне 0..255",
      "dashboard.create_in_progress": "Создаем пользователя Xray и URI...",
      "dashboard.create_success": "Клиент создан",
      "dashboard.create_empty_uri": "Клиент создан, но URI пустой. Укажите XRAY_PUBLIC_* в .env",
      "dashboard.create_failed": "Не удалось создать ключ клиента.",
      "dashboard.action_failed": "Действие не выполнено. Проверьте Xray и БД.",
      "dashboard.resync_completed": "Ресинк завершен",
      "dashboard.reset_completed": "Сброс трафика пользователей завершен",
      "panel.breadcrumbs": "Главная | Настройки панели",
      "panel.title": "Настройки панели",
      "panel.subtitle": "Оформление, обновление, таблица клиентов и поведение графиков",
      "panel.security_title": "Предупреждение безопасности",
      "panel.security_text": "Соединение не зашифровано. Используйте HTTPS перед вводом чувствительных данных.",
      "panel.cpu": "CPU",
      "panel.memory": "Память",
      "panel.online_ratio": "Доля онлайн",
      "panel.appearance": "Оформление",
      "panel.theme_mode": "Режим темы",
      "panel.switch_theme": "Сменить тему",
      "panel.compact_mode": "Компактный режим",
      "panel.show_notifications": "Показывать уведомления",
      "panel.dashboard": "Дашборд",
      "panel.refresh_period": "Период обновления (сек)",
      "panel.auto_copy_uri": "Автокопирование URI после создания",
      "panel.clients_rows_limit": "Лимит строк клиентов",
      "panel.default_sort": "Сортировка по умолчанию",
      "panel.default_filter": "Фильтр по умолчанию",
      "panel.graphs": "Графики",
      "panel.polling_interval": "Интервал опроса (сек)",
      "panel.line_width": "Толщина линии (2-6)",
      "panel.history_points": "Точек истории (30-180)",
      "panel.save_all": "Сохранить все настройки",
      "panel.service_status": "Статус сервисов",
      "panel.database": "База данных",
      "panel.xray_stats_api": "Xray Stats API",
      "panel.active_keys": "Активные ключи",
      "panel.online_users": "Пользователи онлайн",
      "panel.connected": "Подключено",
      "panel.error": "Ошибка",
      "panel.enabled": "Включено",
      "panel.disabled": "Отключено",
      "panel.saved_ok": "Настройки панели сохранены",
      "panel.saved_hint": "Настройки сохранены. Перезагрузите dashboard/graphs для применения интервалов.",
      "panel.status_load_failed": "Не удалось загрузить статус панели",
      "graphs.breadcrumbs": "Главная | Графики",
      "graphs.title": "Живые графики",
      "graphs.subtitle": "Метрики сервера и Xray на отдельных графиках",
      "graphs.server_metrics": "Метрики сервера",
      "graphs.xray_metrics": "Метрики Xray",
      "graphs.cpu_percent": "CPU %",
      "graphs.memory_percent": "Память %",
      "graphs.inbound_traffic": "Входящий трафик",
      "graphs.users_traffic": "Трафик пользователей",
      "graphs.active_keys": "Активные ключи",
      "graphs.online_users": "Пользователи онлайн",
      "graphs.live_status": "Live • Ключи {keys} • Онлайн {online} • CPU {cpu}%",
      "graphs.live_unavailable": "Сейчас недоступны live-данные.",
      "login.title": "Добро пожаловать в Lunet Panel",
      "login.subtitle": "Войдите для управления Xray",
      "login.username": "Логин",
      "login.password": "Пароль",
      "login.submit": "Войти",
      "login.failed": "Ошибка входа. Проверьте логин и пароль.",
      "xray.title": "Настройки Xray",
      "xray.breadcrumbs": "Главная | Настройки Xray",
      "xray.subtitle": "Понятный статус, редактирование конфига и API для разработчиков",
      "xray.save": "Сохранить конфиг",
      "xray.restart": "Перезапустить Xray",
      "xray.resync": "Синхронизировать",
      "xray.runtime": "Сводка runtime",
      "xray.dependencies": "Зависимости",
      "xray.database": "База данных",
      "xray.config": "Xray config.json",
      "xray.api": "API разработчика (управление Xray)",
      "xray.search_api": "Поиск endpoint...",
      "xray.format_json": "Форматировать JSON",
      "xray.validate": "Проверить",
      "xray.keys_title": "Ключи Xray",
      "xray.public_key": "Публичный ключ",
      "xray.private_key": "Приватный ключ",
      "xray.short_id": "Short ID",
      "xray.copy": "Копировать",
      "xray.db_short": "БД",
      "xray.stats_api_short": "Stats API",
      "xray.inbounds_short": "Инбаунды",
      "xray.outbounds_short": "Аутбаунды",
      "xray.method": "Метод",
      "xray.path": "Путь",
      "xray.auth": "Авторизация",
      "xray.description": "Описание",
      "xray.k_xray_addr": "Адрес Xray",
      "xray.k_inbound_tag": "Тег inbound",
      "xray.k_sync_server_id": "ID сервера синхронизации",
      "xray.k_config_path": "Путь к конфигу",
      "xray.k_routing_rules": "Правил маршрутизации",
      "xray.k_api_enabled": "API включен",
      "xray.k_log_level": "Уровень логов",
      "xray.k_config_error": "Ошибка конфига",
      "xray.k_missing": "Отсутствует",
      "xray.k_stats_available": "Статистика доступна",
      "xray.missing_none": "нет",
      "xray.read_config_failed": "Не удалось прочитать конфиг Xray.",
      "xray.json_formatted": "JSON отформатирован",
      "xray.invalid_json": "Неверный формат JSON.",
      "xray.json_valid": "JSON корректный",
      "xray.json_invalid": "JSON некорректный",
      "xray.saving": "Сохраняем конфиг...",
      "xray.config_saved": "Конфиг сохранен",
      "xray.save_failed": "Не удалось сохранить конфиг Xray.",
      "xray.restarting": "Перезапуск Xray...",
      "xray.restart_failed": "Не удалось перезапустить Xray.",
      "xray.resync_progress": "Выполняется ресинк...",
      "xray.resync_done": "Ресинк завершен: синхронизировано {synced}, ошибок {failed}",
      "xray.saved_ok": "Конфиг Xray успешно сохранен",
      "xray.restart_ok": "Xray перезапущен",
      "xray.resync_failed": "Не удалось синхронизировать. Проверьте БД и Xray.",
    },
  };

  function getLang() {
    return (localStorage.getItem(LANG_KEY) || "en").toLowerCase() === "ru" ? "ru" : "en";
  }

  function t(key, fallback) {
    const lang = getLang();
    return (TRANSLATIONS[lang] && TRANSLATIONS[lang][key]) || fallback || key;
  }

  function applyTheme(theme) {
    const resolved = theme === "light" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", resolved);
    localStorage.setItem(THEME_KEY, resolved);
    document.querySelectorAll("[data-theme-toggle]").forEach((el) => {
      el.textContent = resolved === "dark" ? t("common.theme_light", "Light theme") : t("common.theme_dark", "Dark theme");
    });
  }

  function initTheme() {
    applyTheme(localStorage.getItem(THEME_KEY) || "dark");
  }

  function bindThemeToggle() {
    document.querySelectorAll("[data-theme-toggle]").forEach((el) => {
      el.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme");
        applyTheme(current === "dark" ? "light" : "dark");
      });
    });
  }

  function applyLang(lang) {
    const resolved = (lang || "en").toLowerCase() === "ru" ? "ru" : "en";
    localStorage.setItem(LANG_KEY, resolved);
    document.documentElement.setAttribute("data-lang", resolved);
    document.documentElement.lang = resolved;

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (key) el.textContent = t(key, el.textContent);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      if (key) el.setAttribute("placeholder", t(key, el.getAttribute("placeholder") || ""));
    });
    document.querySelectorAll("[data-lang-toggle]").forEach((el) => {
      el.textContent = resolved === "en" ? "RU" : "EN";
    });

    applyTheme(localStorage.getItem(THEME_KEY) || "dark");
    document.dispatchEvent(new CustomEvent("lunet:lang-changed", { detail: { lang: resolved } }));
  }

  function initLang() {
    applyLang(getLang());
  }

  function bindLangToggle() {
    document.querySelectorAll("[data-lang-toggle]").forEach((el) => {
      el.addEventListener("click", () => {
        applyLang(getLang() === "en" ? "ru" : "en");
      });
    });
  }

  function bindStorageSync() {
    window.addEventListener("storage", (event) => {
      if (event.key === LANG_KEY) {
        applyLang(event.newValue || "en");
      }
      if (event.key === THEME_KEY) {
        applyTheme(event.newValue || "dark");
      }
    });
  }

  function ensureToastRoot() {
    let root = document.getElementById("toastRoot");
    if (!root) {
      root = document.createElement("div");
      root.id = "toastRoot";
      root.className = "toast-root";
      document.body.appendChild(root);
    }
    return root;
  }

  function getPrefs() {
    try {
      const parsed = JSON.parse(localStorage.getItem(PREFS_KEY) || "{}");
      return { ...DEFAULT_PREFS, ...(parsed || {}) };
    } catch {
      return { ...DEFAULT_PREFS };
    }
  }

  function setPrefs(next) {
    const merged = { ...getPrefs(), ...(next || {}) };
    localStorage.setItem(PREFS_KEY, JSON.stringify(merged));
    return merged;
  }

  function showToast(message, type) {
    if (!getPrefs().show_toasts) return;
    const root = ensureToastRoot();
    const item = document.createElement("div");
    item.className = `toast ${type || "info"}`;
    item.textContent = message;
    root.appendChild(item);
    setTimeout(() => item.remove(), 3600);
  }

  function humanError(error, fallback) {
    const text = String(error || "").toLowerCase();
    if (text.includes("401")) return t("common.session_expired", "Session expired. Please login again.");
    if (text.includes("already exists")) return t("common.already_exists", "This user already has an active key.");
    if (text.includes("connection") || text.includes("timeout")) return t("common.connection_error", "Cannot reach backend/Xray service.");
    if (text.includes("permission denied")) return t("common.permission_denied", "Permission denied for this action.");
    if (text.includes("invalid")) return t("common.input_invalid", "Input is invalid. Please check the fields.");
    return fallback || t("common.operation_failed", "Operation failed. Try again.");
  }

  function applyPrefs() {
    const prefs = getPrefs();
    if (document.body) {
      document.body.classList.toggle("compact", !!prefs.compact_mode);
    }
    return prefs;
  }

  function installSelectValueHook() {
    if (window.__lunetSelectValueHookInstalled) return;
    const descriptor = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value");
    if (!descriptor || !descriptor.get || !descriptor.set) return;

    Object.defineProperty(HTMLSelectElement.prototype, "value", {
      configurable: descriptor.configurable,
      enumerable: descriptor.enumerable,
      get() {
        return descriptor.get.call(this);
      },
      set(next) {
        descriptor.set.call(this, next);
        if (typeof this.__lunetSyncSelect === "function") {
          this.__lunetSyncSelect();
        }
      },
    });
    window.__lunetSelectValueHookInstalled = true;
  }

  function enhanceSelect(selectEl) {
    if (!selectEl || selectEl.__lunetEnhanced) return;
    if (selectEl.multiple || Number(selectEl.size || 0) > 1) return;

    selectEl.__lunetEnhanced = true;
    selectEl.classList.add("lunet-native-select");

    const root = document.createElement("div");
    root.className = "lunet-select";

    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "lunet-select-trigger";
    trigger.setAttribute("aria-haspopup", "listbox");
    trigger.setAttribute("aria-expanded", "false");

    const triggerLabel = document.createElement("span");
    triggerLabel.className = "lunet-select-label";
    trigger.appendChild(triggerLabel);

    const menu = document.createElement("div");
    menu.className = "lunet-select-menu";
    menu.setAttribute("role", "listbox");

    function closeMenu() {
      root.classList.remove("open");
      trigger.setAttribute("aria-expanded", "false");
    }

    function openMenu() {
      root.classList.add("open");
      trigger.setAttribute("aria-expanded", "true");
    }

    function rebuildOptions() {
      menu.innerHTML = "";
      Array.from(selectEl.options).forEach((opt) => {
        const item = document.createElement("button");
        item.type = "button";
        item.className = "lunet-select-option";
        item.textContent = opt.textContent || opt.label || "";
        item.dataset.value = opt.value;
        item.setAttribute("role", "option");
        item.setAttribute("aria-selected", opt.selected ? "true" : "false");
        if (opt.disabled) {
          item.disabled = true;
        }
        if (opt.selected) {
          item.classList.add("active");
        }
        item.addEventListener("click", () => {
          if (opt.disabled) return;
          selectEl.value = opt.value;
          selectEl.dispatchEvent(new Event("change", { bubbles: true }));
          selectEl.dispatchEvent(new Event("input", { bubbles: true }));
          syncFromSelect();
          closeMenu();
        });
        menu.appendChild(item);
      });
    }

    function syncFromSelect() {
      const selected = selectEl.options[selectEl.selectedIndex];
      triggerLabel.textContent = selected ? selected.textContent || selected.label || "" : "";
      Array.from(menu.children).forEach((el) => {
        const node = el;
        const active = node.dataset.value === selectEl.value;
        node.classList.toggle("active", active);
        node.setAttribute("aria-selected", active ? "true" : "false");
      });
      trigger.disabled = !!selectEl.disabled;
      root.classList.toggle("disabled", !!selectEl.disabled);
    }

    selectEl.__lunetSyncSelect = () => {
      rebuildOptions();
      syncFromSelect();
    };

    trigger.addEventListener("click", () => {
      if (root.classList.contains("open")) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    document.addEventListener("click", (event) => {
      if (!root.contains(event.target)) {
        closeMenu();
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeMenu();
      }
    });

    selectEl.addEventListener("change", syncFromSelect);
    selectEl.addEventListener("input", syncFromSelect);

    selectEl.insertAdjacentElement("afterend", root);
    root.appendChild(trigger);
    root.appendChild(menu);
    rebuildOptions();
    syncFromSelect();
  }

  function enhanceSelects() {
    installSelectValueHook();
    document.querySelectorAll("select").forEach((selectEl) => enhanceSelect(selectEl));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", enhanceSelects, { once: true });
  } else {
    enhanceSelects();
  }

  document.addEventListener("lunet:lang-changed", () => {
    document.querySelectorAll("select").forEach((selectEl) => {
      if (typeof selectEl.__lunetSyncSelect === "function") {
        selectEl.__lunetSyncSelect();
      }
    });
  });

  window.LunetTheme = { initTheme, bindThemeToggle, applyTheme };
  window.LunetI18n = { initLang, bindLangToggle, bindStorageSync, applyLang, getLang, t };
  window.LunetUI = { showToast, humanError, getPrefs, setPrefs, applyPrefs, enhanceSelects };
})();
