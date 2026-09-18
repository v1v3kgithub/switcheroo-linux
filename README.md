# Switcheroo for Linux Mint

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux%20Mint%20%7C%20Ubuntu-brightgreen.svg)]()
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)]()
[![Toolkit: GTK 3](https://img.shields.io/badge/Toolkit-GTK%203%20%7C%20libwnck-orange.svg)]()

> **The keyboard-driven incremental-search window switcher for Linux Mint (Cinnamon).**

Switcheroo is designed for anyone who spends more time using a keyboard than a mouse. Instead of cycling through dozens of open windows with Alt+Tab, Switcheroo lets you quickly jump to any window by typing just a few characters of its title or application name.

A native Linux port inspired by [Switcheroo for Windows](https://github.com/kvakulo/Switcheroo) by James Sulak and Regin Larsen, built natively with **Python 3**, **GTK 3**, and **libwnck**.

---

## Features

- ⚡ **Instant Incremental Search**: Centered floating overlay that appears immediately upon pressing your global hotkey.
- 🎯 **Multi-Tier Match Scoring**:
  - **Exact Prefix** (Score 4)
  - **Significant Characters / Acronyms / CamelCase** (Score 2, e.g., `fx` matches `Firefox`, `vsc` matches `Visual Studio Code`)
  - **Substring** (Score 2)
  - **Fuzzy Subsequence** (Score 1)
- 🔤 **Live Match Highlighting**: Characters contributing to the search result are rendered in **bold**, making matching transparent.
- 🔍 **Dot Syntax Filter**:
  - `query`: Matches against both window title and process name.
  - `<process>.<title>` (e.g. `code.main` or `subl.rb`): Restricts process name to the left side and title to the right side.
  - `.<title>` (leading dot, e.g. `.log`): Automatically pins the search to the **foreground window's application**!
- ⌨️ **Keyboard Controls**:
  - `Enter` / Double Click: Switch to and raise the selected window.
  - `Ctrl + W` / `Alt + X`: Gracefully close the selected window directly from the switcher.
  - `Tab` / `Shift + Tab` or `↑` / `↓`: Navigate list.
  - `Alt + J` / `Alt + K`: Vim-style navigation.
  - `Esc` / Focus Out: Dismiss the switcher.
- 🔄 **Smart MRU Sorting**: Moves the currently active window to the bottom, so pressing your hotkey + `Enter` immediately toggles back to the previous window (classic Alt+Tab muscle memory).
- 🐧 **Native Cinnamon Integration**:
  - Embedded system tray icon (AyatanaAppIndicator) with *Run on Startup* toggle, *About*, and *Quit*.
  - Matches Linux Mint themes, fonts, and dark mode automatically.
- 🚀 **Zero Extra Dependencies on Linux Mint 22.3**: Uses system libraries already shipping with Cinnamon.

---

## Keyboard Shortcuts

| Action | Shortcut | Remarks |
| :--- | :--- | :--- |
| **Activate Switcher** | `Alt + Space` | Customizable in `~/.config/switcheroo/config.json` |
| **Switch to Window** | `Enter` | Raises and focuses the selected window |
| **Close Window** | `Ctrl + W` or `Alt + X` | Closes the selected window gracefully |
| **Navigate List Down** | `↓`, `Tab`, or `Alt + J` | Cycles through matching windows |
| **Navigate List Up** | `↑`, `Shift + Tab`, or `Alt + K` | Cycles backwards |
| **Filter by Active App** | `.<query>` | Leading dot filters only within the active app's windows |
| **Dismiss Overlay** | `Esc` or clicking away | Closes Switcheroo without switching |

---

## Installation

### Prerequisites (Linux Mint & Ubuntu)
All required system packages are pre-installed by default on Linux Mint Cinnamon. On minimal systems or standard Ubuntu, ensure they are present:

```bash
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-wnck-3.0 gir1.2-keybinder-3.0 gir1.2-ayatanaappindicator3-0.1
```

### 1-Step Quick Install

Clone this repository and run the automated installer:

```bash
git clone https://github.com/v1v3kgithub/switcheroo-linux.git
cd switcheroo-linux
./install.sh
```

The installer will:
1. Validate required system libraries.
2. Install the `switcheroo` command to `~/.local/bin/`.
3. Install high-resolution application icons to `~/.local/share/icons/`.
4. Register the desktop launcher in `~/.local/share/applications/` so it appears in the Linux Mint Application Menu.

### Python pip Install

Alternatively, install using standard pip:

```bash
pip install --user .
```

---

## Running Switcheroo

Start Switcheroo from your terminal or application menu:

```bash
switcheroo
```

Switcheroo will run as a background daemon with an icon in your system tray. Press `Alt + Space` anytime to summon the switcher.

### CLI Options

```bash
switcheroo --show      # Show switcher overlay immediately
switcheroo --toggle    # Toggle visibility of the overlay
switcheroo --quit      # Terminate running background daemon
switcheroo --verbose   # Run with debug logging
```

---

## Configuration

Settings are saved in `~/.config/switcheroo/config.json`:

```json
{
  "hotkey": "<Alt>space",
  "autostart": false,
  "max_results": 12,
  "window_width": 560,
  "show_help": false
}
```

- **`hotkey`**: Any GTK/Keybinder shortcut specification (e.g. `<Super>space`, `<Alt>Tab`, `<Control><Alt>s`).
- **`autostart`**: Set to `true` to start automatically upon login (can also be toggled via the system tray menu).

---

## Uninstallation

To cleanly remove Switcheroo, its desktop entries, and its icons:

```bash
./uninstall.sh
```

---

## Running Tests

Run the test suite to verify matching, scoring, and dot-syntax parsing:

```bash
python3 -m unittest discover tests/ -v
```

---

## Credits & License

- **Ported for Linux Mint** by Vivek.
- **Original Windows Concept & Code** by [James Sulak](https://github.com/jsulak) and [Regin Larsen](https://github.com/kvakulo) ([kvakulo/Switcheroo](https://github.com/kvakulo/Switcheroo)).
- Licensed under the [GNU General Public License v3.0](LICENSE).
