# Lunet Panel

Панель управления Xray с web-интерфейсом, авторизацией, созданием ключей, статистикой трафика, online-статусами и графиками.

## Быстрая установка на сервер (вместе с Xray)

```bash
git clone <repo-url> /opt/lunet-panel
cd /opt/lunet-panel
sudo bash scripts/install_lunet_panel.sh
```

## Точка входа агента

- основной entrypoint: `agent_main.py`
- запуск локально:

```bash
python agent_main.py
```

Скрипт автоматически:
- ставит зависимости Python;
- ставит Xray (если не установлен);
- поднимает systemd-сервис `lunet-panel`;
- включает `xray` и `lunet-panel`.

## Основные ENV

- `XRAY_DB_DSN` - строка подключения к Postgres.
- `XRAY_ADDR` - gRPC адрес Xray.
- `XRAY_CONFIG_PATH` - путь к `config.json` Xray.
- `XRAY_RESTART_CMD` - команда перезапуска Xray, пример: `systemctl restart xray`.
- `XRAY_WEB_USERNAME`, `XRAY_WEB_PASSWORD` - логин в web.
- `XRAY_PUBLIC_HOST`, `XRAY_PUBLIC_PORT`, `XRAY_VLESS_SNI`, `XRAY_VLESS_PBK`, `XRAY_VLESS_SID` - генерация URI при создании ключа.

## API для разработчиков (Xray management)

Полный список доступен в панели: `Xray Settings -> Developer API`.

- `POST /add_user` - добавить пользователя в Xray inbound (Bearer).
- `POST /remove_user` - удалить пользователя по email (Bearer).
- `POST /resync` - пересинхронизировать активные ключи из БД в Xray (Bearer).
- `GET /web/api/dashboard` - данные dashboard (Cookie session).
- `POST /web/api/keys` - создать ключ + пользователя в Xray + URI (Cookie).
- `GET /web/api/xray/settings` - состояние Xray/зависимостей/summary (Cookie).
- `GET /web/api/xray/config` - прочитать `config.json` Xray (Cookie).
- `PUT /web/api/xray/config` - обновить `config.json` Xray (Cookie).
- `POST /web/api/xray/restart` - перезапустить Xray (Cookie).
- `POST /web/api/xray/resync` - resync из UI (Cookie).
- `POST /web/api/resets/traffic` - reset counters (Cookie).
- `GET /web/api/graphs/live` - live-метрики для графиков (Cookie).
