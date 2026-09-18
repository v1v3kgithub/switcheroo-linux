# Switcheroo for Linux Mint

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux%20Mint%20%7C%20Ubuntu-brightgreen.svg)]()
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)]()
[![Toolkit: GTK 3](https://img.shields.io/badge/Toolkit-GTK%203%20%7C%20libwnck-orange.svg)]()

> **The keyboard-driven incremental-search window switcher for Linux Mint (Cinnamon).**

Switcheroo is designed for anyone who spends more time using a keyboard than a mouse. Instead of cycling through dozens of open windows with Alt+Tab, Switcheroo lets you instantly jump to any window by typing just a few characters of its title or application name.

---

## 📌 Origin & Attribution

This project is a native Linux rewrite of the open-source Windows application **[Switcheroo](https://github.com/kvakulo/Switcheroo)**, originally created by **[James Sulak](https://github.com/jsulak)** and maintained by **[Regin Larsen](https://github.com/kvakulo)**.

While the original application was built with C# and WPF for the Windows API, this Linux port faithfully replicates its 4-tier matching algorithms, MRU window reordering, and dot-query syntax using **Python 3**, **GTK 3**, and **libwnck-3.0**.

---

## 🧩 Required Dependencies

### Linux Mint 22 / Ubuntu 24.04 (Cinnamon / GNOME / X11)
On Linux Mint Cinnamon, all core libraries are **pre-installed by default**. On minimal systems or standard Ubuntu, install the required packages using `apt`:

```bash
sudo apt update
sudo apt install -y python3 python3-gi gir1.2-gtk-3.0 gir1.2-wnck-3.0 gir1.2-keybinder-3.0 gir1.2-ayatanaappindicator3-0.1
```

### Dependency Breakdown
| Library / Package | Purpose |
| :--- | :--- |
| **`python3`** (>= 3.8) | Application runtime environment |
| **`python3-gi`** (PyGObject) | Python bindings for GObject-based C libraries |
| **`gir1.2-gtk-3.0`** | GTK 3 graphical user interface toolkit |
| **`gir1.2-wnck-3.0`** (libwnck) | Window Navigator Construction Kit for window discovery, icons, switching, and closing |
| **`gir1.2-keybinder-3.0`** | Global X11 keyboard shortcut management (`Alt + Space`) |
| **`gir1.2-ayatanaappindicator3-0.1`** | System tray notification area indicator |

To verify that all dependencies are ready on your system, run:
```bash
python3 -c "import gi; gi.require_version('Gtk', '3.0'); gi.require_version('Wnck', '3.0'); gi.require_version('Keybinder', '3.0'); print('✓ All dependencies present!')"
```

---

## 📦 Installation & Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/v1v3kgithub/switcheroo-linux.git
cd switcheroo-linux
```

### Step 2: Run the Installer
Run the automated user installation script:
```bash
./install.sh
```

The installer will:
1. Validate required system libraries.
2. Install application files to `~/.local/share/switcheroo/`.
3. Create the executable launcher in `~/.local/bin/switcheroo`.
4. Install the application icon to `~/.local/share/icons/hicolor/48x48/apps/`.
5. Register `switcheroo.desktop` in `~/.local/share/applications/` so it appears in your Linux Mint Application Menu.

> **Note**: Ensure `~/.local/bin` is in your `$PATH`. If not, add this line to your `~/.bashrc`:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```

---

## 🚀 Running Switcheroo

Start the background daemon from your terminal or application launcher:

```bash
switcheroo
```

Switcheroo runs in the background with an icon in your system tray. Press **`Alt + Space`** anytime to summon the switcher!

### Daemon Commands & Options
```bash
switcheroo --show      # Show the switcher window immediately
switcheroo --toggle    # Toggle visibility of the switcher window
switcheroo --quit      # Terminate running background daemon
switcheroo --verbose   # Run with debug logging in terminal
```

---

## ⌨️ Keyboard Shortcuts & Usage

| Action | Shortcut | Remarks |
| :--- | :--- | :--- |
| **Activate Switcher** | `Alt + Space` | Global hotkey (customizable in `config.json`) |
| **Switch to Window** | `Enter` or Double-Click | Raises and gives focus to the highlighted window |
| **Close Window** | `Ctrl + W` or `Alt + X` | Gracefully closes the highlighted window directly |
| **Navigate Down** | `↓`, `Tab`, or `Alt + J` | Cycles forward through matching windows |
| **Navigate Up** | `↑`, `Shift + Tab`, or `Alt + K` | Cycles backward through matching windows |
| **Filter by Active App** | `.<query>` | Leading dot filters only within the active app's windows |
| **Restrict Process & Title** | `<proc>.<title>` | e.g. `code.main` matches process "code" and title "main" |
| **Dismiss Switcher** | `Esc` or Click Outside | Closes Switcheroo without switching |

---

## 🛠️ Development: Checking Out Code & Making Changes

If you want to contribute or modify Switcheroo:

### 1. Clone & Set Up
```bash
git clone https://github.com/v1v3kgithub/switcheroo-linux.git
cd switcheroo-linux
```

### 2. Run Directly from Source (No Installation Needed)
You can run and test your changes directly against the source tree using `run.py`:

```bash
# Launch background daemon directly from local code
python3 run.py --verbose

# Or trigger the overlay immediately
python3 run.py --show
```

### 3. Project Structure
```
switcheroo-linux/
├── switcheroo/
│   ├── app.py              # Application lifecycle, IPC socket daemon, CLI parsing
│   ├── config.py           # Settings loader/saver (~/.config/switcheroo/config.json)
│   ├── hotkey.py           # libkeybinder3 global shortcut listener
│   ├── tray.py             # AyatanaAppIndicator system tray icon and menu
│   ├── autostart.py        # Desktop autostart entry manager
│   ├── core/
│   │   ├── filterer.py     # Query parser (handles '.', 'proc.title') and ranking coordinator
│   │   ├── highlighter.py  # Pango markup generator (<b>highlighted text</b>)
│   │   ├── window_finder.py# libwnck desktop window discovery and MRU reordering
│   │   ├── window_model.py # AppWindow data structure
│   │   └── matchers/       # The 4 matching algorithms
│   │       ├── starts_with.py   # StartsWithMatcher (Score: 4)
│   │       ├── significant.py   # SignificantCharactersMatcher (Score: 2)
│   │       ├── contains.py      # ContainsMatcher (Score: 2)
│   │       └── fuzzy.py         # IndividualCharactersMatcher (Score: 1)
│   └── ui/
│       ├── window.py       # GTK 3 overlay window, list display, keyboard navigation
│       ├── x11_focus.py    # X11 EWMH pager activation and focus-stealing bypass
│       └── style.css       # GTK CSS styling
├── tests/
│   ├── test_matchers.py    # Unit tests for matching algorithms
│   └── test_filterer.py    # Unit tests for query syntax and scoring
├── run.py                  # Direct source runner
├── install.sh              # User installer script
├── uninstall.sh            # User uninstaller script
└── pyproject.toml          # Python packaging specification
```

### 4. Running Unit Tests
Switcheroo includes a unit test suite verifying string matching, scoring, and query parsing:

```bash
python3 -m unittest discover -s tests -v
```

### 5. Reinstalling After Making Changes
Once you have tested your changes with `python3 run.py`, apply them to your user environment:

```bash
# Stop running daemon
switcheroo --quit 2>/dev/null || true

# Reinstall updated files
./install.sh

# Restart daemon
switcheroo
```

---

## ⚙️ Configuration

Preferences are stored in `~/.config/switcheroo/config.json`:

```json
{
  "hotkey": "<Alt>space",
  "autostart": false,
  "max_results": 12,
  "window_width": 560,
  "show_help": false
}
```

- **`hotkey`**: Any valid Keybinder shortcut string (e.g. `<Super>space`, `<Control><Alt>s`, `<Alt>Tab`).
- **`autostart`**: `true` launches Switcheroo on user login (also toggleable via the system tray icon).

---

## 🗑️ Uninstallation

To cleanly remove Switcheroo, its desktop launcher, and all associated assets:

```bash
./uninstall.sh
```

---

## 📄 License & Credits

- **Ported & Maintained for Linux Mint** by the Open Source Community.
- **Original Windows Switcheroo** Copyright © James Sulak and Regin Larsen ([kvakulo/Switcheroo](https://github.com/kvakulo/Switcheroo)).
- Licensed under the [GNU General Public License v3.0](LICENSE).
