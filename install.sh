#!/usr/bin/env bash
set -e

echo "==========================================="
echo " Installing Switcheroo for Linux Mint"
echo "==========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/48x48/apps"
DATA_DIR="$HOME/.local/share/switcheroo"

# 1. Check Python and GObject Introspection dependencies
echo "-> Checking system dependencies..."
python3 -c "
import sys
missing = []
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except Exception:
    missing.append('gir1.2-gtk-3.0')

try:
    import gi
    gi.require_version('Wnck', '3.0')
    from gi.repository import Wnck
except Exception:
    missing.append('gir1.2-wnck-3.0')

try:
    import gi
    gi.require_version('Keybinder', '3.0')
    from gi.repository import Keybinder
except Exception:
    missing.append('gir1.2-keybinder-3.0')

if missing:
    print('Missing system libraries:', ' '.join(missing))
    print('On Linux Mint / Ubuntu, install with:')
    print('  sudo apt install python3-gi ' + ' '.join(missing))
    sys.exit(1)
" || exit 1

echo "✓ System dependencies verified!"

# 2. Install application package into ~/.local/share/switcheroo
echo "-> Installing application files to $DATA_DIR..."
mkdir -p "$DATA_DIR"
rm -rf "$DATA_DIR/switcheroo"
cp -r "$SCRIPT_DIR/switcheroo" "$DATA_DIR/"

# 3. Create launcher script in ~/.local/bin/switcheroo
mkdir -p "$BIN_DIR"
echo "-> Creating CLI launcher in $BIN_DIR/switcheroo..."
cat << 'EOF' > "$BIN_DIR/switcheroo"
#!/usr/bin/env bash
export PYTHONPATH="$HOME/.local/share/switcheroo:$PYTHONPATH"
exec /usr/bin/python3 -m switcheroo.app "$@"
EOF
chmod +x "$BIN_DIR/switcheroo"

# 4. Install Icon
mkdir -p "$ICON_DIR"
if [ -f "$SCRIPT_DIR/assets/switcheroo.png" ]; then
    echo "-> Installing application icon..."
    cp "$SCRIPT_DIR/assets/switcheroo.png" "$ICON_DIR/switcheroo.png"
fi

# 5. Install Desktop File
mkdir -p "$APP_DIR"
echo "-> Installing desktop launcher to $APP_DIR..."
sed "s|Exec=switcheroo|Exec=$BIN_DIR/switcheroo|g" "$SCRIPT_DIR/data/switcheroo.desktop" > "$APP_DIR/switcheroo.desktop"
chmod +x "$APP_DIR/switcheroo.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DIR" >/dev/null 2>&1 || true
fi

echo ""
echo "==========================================="
echo "✓ Switcheroo Installed Successfully!"
echo "==========================================="
echo "You can now run Switcheroo:"
echo "  - From terminal: switcheroo"
echo "  - From Application Menu: Search 'Switcheroo'"
echo "  - Global Hotkey: Alt + Space (customizable in ~/.config/switcheroo/config.json)"
echo ""
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Notice: '$BIN_DIR' is not currently in your PATH."
    echo "Add it to your environment by adding this line to ~/.bashrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi
