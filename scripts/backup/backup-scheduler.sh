#!/usr/bin/env bash
# Backup scheduler setup (systemd for Linux, launchd for macOS)
set -euo pipefail

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$INSTALL_DIR/backup-restore.sh"

setup_systemd(){
  SERVICE_FILE="/etc/systemd/system/dotfiles-backup.service"
  TIMER_FILE="/etc/systemd/system/dotfiles-backup.timer"
  echo "Creating systemd service..."
  cat > "$SERVICE_FILE" <<EOS
[Unit]
Description=Dotfiles Backup Service
After=network-online.target

[Service]
Type=oneshot
ExecStart=$SCRIPT backup
EOS
  echo "Creating systemd timer (daily at 02:00)..."
  cat > "$TIMER_FILE" <<EOS
[Unit]
Description=Run dotfiles backup daily

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOS
  systemctl daemon-reload
  systemctl enable --now dotfiles-backup.timer
  echo "Systemd backup timer enabled."
}

setup_launchd(){
  PLIST="${HOME}/Library/LaunchAgents/com.dotfiles.backup.plist"
  echo "Creating launchd plist..."
  cat > "$PLIST" <<EOS
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.dotfiles.backup</string>
    <key>ProgramArguments</key><array><string>$SCRIPT</string><string>backup</string></array>
    <key>StartCalendarInterval</key><dict>
        <key>Hour</key><integer>2</integer>
        <key>Minute</key><integer>0</integer>
    </dict>
    <key>StandardOutPath</key><string>/tmp/dotfiles-backup.log</string>
    <key>StandardErrorPath</key><string>/tmp/dotfiles-backup.err</string>
    <key>RunAtLoad</key><true/>
</dict>
</plist>
EOS
  launchctl load -w "$PLIST"
  echo "Launchd backup job installed."
}

# Detect platform
OS=$(uname -s)
if [[ "$OS" == "Linux" ]]; then
  if command -v systemctl >/dev/null 2>&1; then
    setup_systemd
  else
    echo "Systemd not available. Cannot install scheduler."
    exit 1
  fi
elif [[ "$OS" == "Darwin" ]]; then
  setup_launchd
else
  echo "Unsupported OS: $OS"
  exit 1
fi
