#!/usr/bin/env bash
set -e

echo "==========================================="
echo " Uninstalling Switcheroo for Linux Mint"
echo "==========================================="

BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/48x48/apps"
AUTOSTART_DIR="$HOME/.config/autostart"

# 1. Stop any running daemon
if command -v switcheroo >/dev/null 2>&1; then
    switcheroo --quit 2>/dev/null || true
fi

# 2. Uninstall package
python3 -m pip uninstall -y switcheroo-linux 2>/dev/null || true

# 3. Remove files
rm -f "$BIN_DIR/switcheroo"
rm -f "$APP_DIR/switcheroo.desktop"
rm -f "$ICON_DIR/switcheroo.png"
rm -f "$AUTOSTART_DIR/switcheroo.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DIR" >/dev/null 2>&1 || true
fi

echo "✓ Switcheroo has been successfully uninstalled."
