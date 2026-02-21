#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root: sudo bash scripts/install_lunet_panel.sh"
  exit 1
fi

echo "[1/5] Installing system dependencies..."
apt-get update
apt-get install -y curl unzip python3 python3-venv python3-pip

echo "[2/5] Installing Xray..."
if ! command -v xray >/dev/null 2>&1; then
  bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
else
  echo "Xray already installed"
fi

echo "[3/5] Preparing Lunet Panel runtime..."
mkdir -p /opt/lunet-panel
cp -r . /opt/lunet-panel
cd /opt/lunet-panel
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[4/5] Creating systemd service..."
cat >/etc/systemd/system/lunet-panel.service <<'EOF'
[Unit]
Description=Lunet Panel
After=network.target xray.service
Requires=xray.service

[Service]
Type=simple
WorkingDirectory=/opt/lunet-panel
EnvironmentFile=/opt/lunet-panel/.env
ExecStart=/opt/lunet-panel/.venv/bin/uvicorn agent_main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "[5/5] Enabling services..."
systemctl daemon-reload
systemctl enable --now xray
systemctl enable --now lunet-panel

echo "Done. Panel: http://<server-ip>:8000/web/login"
