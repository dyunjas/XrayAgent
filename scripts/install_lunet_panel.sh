set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root: sudo bash scripts/install_lunet_panel.sh"
  exit 1
fi

echo "[1/5] Installing system dependencies..."
apt-get update
apt-get install -y curl unzip git protobuf-compiler python3 python3-venv python3-pip

echo "[2/5] Installing Xray..."
if ! command -v xray >/dev/null 2>&1; then
  bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
else
  echo "Xray already installed"
fi

echo "[3/6] Preparing Xray protobuf assets..."
if [[ ! -d /opt/xray-protos/proxy || ! -f /opt/xray-protos/proxy/vless/account.proto ]]; then
  rm -rf /opt/xray-protos
  git clone --depth=1 https://github.com/XTLS/Xray-core.git /opt/xray-protos
fi

find /opt/xray-protos -name "*.proto" > /tmp/xray-protos-files.txt
if [[ -s /tmp/xray-protos-files.txt ]]; then
  protoc -I /opt/xray-protos --include_imports \
    --descriptor_set_out=/opt/xray-protos/xray.protoset \
    @/tmp/xray-protos-files.txt
fi

echo "[4/6] Preparing Lunet Panel runtime..."
mkdir -p /opt/lunet-panel
SRC_DIR="$(realpath .)"
DST_DIR="/opt/lunet-panel"
if [[ "${SRC_DIR}" != "${DST_DIR}" ]]; then
  cp -r . "${DST_DIR}"
else
  echo "Source is already ${DST_DIR}, skipping copy"
fi
cd /opt/lunet-panel
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[5/6] Creating/updating systemd service..."
cat >/etc/systemd/system/lunet-panel.service <<'EOF'
[Unit]
Description=Lunet Panel
After=network.target xray.service
Requires=xray.service

[Service]
Type=simple
WorkingDirectory=/opt/lunet-panel
EnvironmentFile=/opt/lunet-panel/.env
Environment=HOST=0.0.0.0
Environment=PORT=8020
ExecStart=/opt/lunet-panel/.venv/bin/python /opt/lunet-panel/agent_main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "[6/6] Enabling services..."
systemctl daemon-reload
systemctl enable --now xray
systemctl enable lunet-panel
systemctl restart lunet-panel

echo "Done. Panel: http://<server-ip>:8020/web/login"
