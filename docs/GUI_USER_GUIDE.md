# TourBox Elite Configuration GUI - User Guide

**Version:** 1.0
**Last Updated:** 2025-11-05

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Understanding the Interface](#understanding-the-interface)
4. [Basic Tasks](#basic-tasks)
5. [Working with Profiles](#working-with-profiles)
6. [Configuring Button Mappings](#configuring-button-mappings)
7. [Tips & Tricks](#tips--tricks)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

The TourBox Elite Configuration GUI is a graphical application that lets you configure your TourBox Elite controller without manually editing configuration files. With this tool, you can:

- **Visually configure** all 20 controls (buttons, dials, scroll wheel, knob)
- **Create application-specific profiles** that automatically switch based on the active window
- **Test configurations** with your physical device before saving
- **Manage multiple profiles** with an intuitive interface

No more editing INI files by hand - everything is point-and-click!

---

## Getting Started

### Prerequisites

Before using the GUI, ensure you have:

1. **Installed the TourBox Elite driver** using `install.sh` (see main README.md)
   - The GUI dependencies are automatically installed by the installer
2. **Configured your device's MAC address** in `~/.config/tourbox/mappings.conf`

> **Note:** If you performed a manual installation, you'll need to install GUI dependencies separately:
> ```bash
> pip install -r tourboxelite/gui/requirements.txt
> ```

### Launching the GUI

Simply run:

```bash
tourbox-gui
```

The installation creates a launcher script that automatically activates the virtual environment and starts the GUI. You can run this command from any directory.

**What happens on launch:**

1. The GUI automatically **stops the TourBox driver** (if running)
2. Shows a progress dialog with status updates
3. Loads your existing configuration from `~/.config/tourbox/mappings.conf`
4. Displays all profiles and button mappings

**On exit:**

- The GUI automatically **restarts the driver** (if it was running before)
- Prompts you to save any unsaved changes

> **Note:** The GUI and driver cannot run at the same time because they both need exclusive access to the TourBox device via Bluetooth.

---

## Understanding the Interface

![TourBox Elite Configuration GUI](images/gui-screenshot.png)

The GUI has a 4-panel layout:

```
┌─────────────────────┬──────────────────────────┐
│                     │                          │
│  1. Controller      │  2. Controls             │
│     View            │     Configuration        │
│                     │     (Button List)        │
│  (Visual TourBox)   │                          │
│                     │                          │
├─────────────────────┼──────────────────────────┤
│                     │                          │
│  3. Profiles        │  4. Control Editor       │
│                     │                          │
│  (Profile List)     │  (Edit Mappings)         │
│                     │                          │
└─────────────────────┴──────────────────────────┘
```

### 1. Controller View (Top-Left)

- **Visual representation** of the TourBox Elite controller
- **Highlights controls** when you select them from the list
- Shows which button you're currently editing

### 2. Profiles (Bottom-Left)

- **List of all available profiles** with window matching rules
- The **default profile** is always present and cannot be deleted
- Shows which windows each profile applies to
- Buttons to **create**, **edit**, and **delete** profiles

### 3. Controls Configuration (Top-Right)

- **Table showing all 20 controls** with their current mappings
- Displays human-readable action names (e.g., "Ctrl+C", "Wheel Up")
- Click any control to **select it for editing**
- Shows "(unmapped)" for controls with no action assigned

### 4. Control Editor (Bottom-Right)

- **Configure the selected control's action**
- Choose action type: Keyboard, Mouse Wheel, or None
- Set modifier keys (Ctrl, Alt, Shift, Super)
- Select keys or mouse wheel directions
- **Apply** button saves changes to memory (not actually saved to the config file yet)

### Menu Bar & Toolbar

- **File Menu:**
  - Save (Ctrl+S) - Write changes to config file
  - Test (Ctrl+T) - Test configuration with physical device
  - Quit - Exit the application

- **Toolbar:** Quick access buttons for Save and Test

- **Status Bar:** Shows current status, profile name, and operation feedback

---

## Basic Tasks

### Task 1: Change a Button Mapping

**Example:** Change the "side" button to Ctrl+C (copy)

1. **Select the profile** you want to edit from the Profiles list (e.g., "default")
2. **Click "side"** in the Controls Configuration table
   - The controller view highlights the side button
   - The Control Editor loads the current mapping
3. In the Control Editor:
   - Select **"Keyboard"** as the action type
   - Check the **"Ctrl"** modifier box
   - Type **"c"** in the text input field
4. Click **"Apply"**
   - The Controls Configuration table updates to show "Ctrl+C"
   - Window title shows an asterisk (*) indicating unsaved changes
5. Click **"Save"** (toolbar or Ctrl+S)
   - Creates a timestamped backup of your config
   - Writes the changes to `~/.config/tourbox/mappings.conf`
   - Success dialog confirms the save

**Result:** The "side" button will now send Ctrl+C when pressed (after restarting the driver or clicking Test).

### Task 2: Create a New Application-Specific Profile

**Example:** Create a profile for Visual Studio Code

1. Click the **"+"** button below the Profiles list
2. In the dialog:
   - Enter profile name: **"vscode"** and click **OK**
   - Choose **Yes** if you would like to copy settings for the currently selected profile
3. The new profile is created and selected
4. A dialog appears asking if you would like to set up window matching rules:
   - Click **Yes** 
   - Click **"Capture Active Window"**
   - I dialog box appears giving you 5 seconds - click on VS Code window
   - The GUI auto-fills the App ID and Window Class fields
   - Click **Apply**
5. Customize button mappings for VS Code (see Task 1)
6. Click **"Save"** to write the profile to config

**Result:** When you focus a VS Code window, this profile automatically activates!

### Task 3: Test Your Configuration

**Example:** Test button mappings with the physical device

1. Make changes to button mappings (see Task 1)
2. Click **"Test"** button (toolbar or Ctrl+T)
   - Changes are automatically saved first
   - Click **OK**
   - GUI becomes disabled except for "Stop Test" button
3. **Press buttons on your physical TourBox**
   - Actions are sent to your system
   - Test that mappings work as expected
4. Click **"Stop Test"** when done
   - GUI re-enables for further editing

**Result:** You can rapidly iterate: edit → test → edit → test without closing the GUI!

---

## Working with Profiles

### What Are Profiles?

Profiles are **collections of button mappings** that can automatically activate based on the active application window. This lets you have different button behaviors for different programs.

**Example use cases:**
- **Default profile:** General mappings for desktop navigation
- **GIMP profile:** Brush size, zoom, undo for image editing
- **Firefox profile:** Tab switching, zoom, page navigation
- **VS Code profile:** Comment code, find, formatting shortcuts

### The Default Profile

- Always present and **cannot be deleted**
- Used when no other profile matches the active window
- Good place to put general-purpose mappings

### Creating Profiles

**Two ways to create a profile:**

1. **Based on selected profile**
   - Copies all button mappings from the currently selected profile
   - Good starting point - customize from there
   - Saves time vs. configuring everything from scratch

2. **Empty profile**
   - No mappings configured
   - All controls show "(unmapped)"
   - Good if you want a completely custom layout

**Steps:**
1. Click **"+"** button
2. Enter a unique name
3. Choose copy or empty
4. Configure window matching rules (next section)

### Window Matching Rules

Profiles activate when the window properties match your rules. You can match by:

- **App ID** - Wayland application identifier (e.g., `code`, `firefox`)
- **Window Class** - X11/Wayland window class (e.g., `firefox-esr`, `Code`)

**Capturing Window Info Automatically:**

1. Click **"⚙"** (settings) button next to a profile
2. Click **"Capture Active Window"** button
3. **Within 5 seconds**, click on the window you want to match
4. The GUI auto-fills the App ID and Window Class fields
5. Edit/clear fields as needed
6. Click **Apply**

**Tips:**
- You can use **one, or both** matching fields
- Any one of the fields must match for the profile to activate
- Leave fields blank to ignore that matching criterion
- We recommend you leave/use both matching methods

### Editing Profiles

1. Select the profile in the Profiles list
2. Click the **"⚙"** (settings) button
3. Edit name and/or window matching rules
4. Click **Apply** (changes saved to memory)
5. Click **Save** button to write to config file

> **Note:** You cannot edit the default profile's settings (name/window matching) - only its button mappings.

### Deleting Profiles

1. Select the profile to delete
2. Click the **"-"** button
3. Confirm deletion in the dialog

> **Warning:** Deletion is permanent!

### Profile Switching

When the TourBox driver is running:

- The driver monitors the active window every 200ms
- Compares window properties against all profile rules
- Switches to the first matching profile
- Falls back to default if no match

**In the GUI:**
- Simply click a profile name to switch to it
- The Controls Configuration table updates
- The Control Editor clears
- Any highlighted control clears

---

## Configuring Button Mappings

### The 20 TourBox Controls

Your TourBox Elite has these controls:

**Buttons (7):**
- `side` - Large side button
- `top` - Top button
- `tall` - Tall button (bottom-left)
- `short` - Short button (bottom-right)
- `c1` - C1 button
- `c2` - C2 button
- `tour` - Tour button (center)

**D-Pad (4):**
- `dpad_up`, `dpad_down`, `dpad_left`, `dpad_right`

**Scroll Wheel (3):**
- `scroll_up` - Scroll wheel up
- `scroll_down` - Scroll wheel down
- `scroll_click` - Press the scroll wheel

**Knob (3):**
- `knob_cw` - Rotate knob clockwise
- `knob_ccw` - Rotate knob counter-clockwise
- `knob_click` - Press the knob

**Dial (3):**
- `dial_cw` - Rotate dial clockwise
- `dial_ccw` - Rotate dial counter-clockwise
- `dial_click` - Press the dial

### Action Types

Each control can be mapped to one of these action types:

#### 1. Keyboard Action

Send a keyboard key press (with optional modifiers).

**Modifiers:** (can combine multiple)
- Ctrl
- Alt
- Shift
- Super (Windows/Command key)

**Keys:**
- **Typeable characters:** Just type them in the text field
  - Letters: a-z (lowercase sends lowercase, uppercase sends uppercase)
  - Numbers: 0-9
  - Symbols: `-` `=` `[` `]` `;` `'` `` ` `` `\` `,` `.` `/`

- **Special keys:** Select from dropdown
  - Control: Enter, Escape, Tab, Space, Backspace, Delete, Insert
  - Arrows: Up, Down, Left, Right
  - Navigation: Home, End, Page Up, Page Down
  - Function: F1-F12
  - Zoom: Zoom In, Zoom Out, Zoom Reset
  - Other: Context Menu

**Examples:**
- `Ctrl+C` - Click Ctrl, type "c"
- `Ctrl+Shift+Z` - Click Ctrl and Shift, type "z"
- `Alt+F4` - Click Alt, select "F4" from dropdown
- `]` - Just type "]" (closing bracket)
- `Super` - Click Super only (no key)

**Tips:**
- Either use the **text input** OR the **dropdown**, not both
- Modifier-only mappings are valid (e.g., just "Ctrl" or "Alt")
- The GUI shows human-readable names in the controls list

#### 2. Mouse Wheel

Simulate mouse wheel scrolling.

**Directions:**
- Vertical Up - Scroll up
- Vertical Down - Scroll down
- Horizontal Left - Scroll left (for apps that support horizontal scrolling)
- Horizontal Right - Scroll right

**Common uses:**
- Map `knob_cw` to Wheel Up and `knob_ccw` to Wheel Down for scrolling
- Map `dial_cw`/`dial_ccw` for zooming (if app supports Ctrl+Wheel)

#### 3. None (Unmapped)

The control does nothing when pressed.

**Use cases:**
- Disable a button you don't use
- Temporarily disable a control while testing
- Prevent accidental presses

---

## Tips & Tricks

### Keyboard Navigation

Speed up your workflow with keyboard shortcuts:

- **Ctrl+S** - Save changes
- **Ctrl+T** - Test configuration
- **Arrow keys** - Navigate between controls in the list
- **Tab** - Move between UI elements

### Workflow Efficiency

**Quick iteration:**
1. Keep the GUI open during setup
2. Use Test mode to try configurations
3. Stop test → tweak → test again
4. No need to restart the GUI

**Bulk editing:**
1. Configure one profile completely
2. Create new profile based on it
3. Change only what's different
4. Saves time vs. configuring from scratch

**Backups:**
- The GUI automatically creates timestamped backups before each save
- Located next to your config: `~/.config/tourbox/mappings.conf.backup.YYYYMMDD_HHMMSS`
- Keeps the 5 most recent backups
- Restore by copying a backup to `mappings.conf`

### Common Mapping Patterns

**Undo/Redo:**
- `short` → Ctrl+Z (undo)
- `tall` → Ctrl+Shift+Z (redo)

**Zoom:**
- `knob_cw` → Ctrl+= (zoom in)
- `knob_ccw` → Ctrl+- (zoom out)

**Scrolling:**
- `dial_cw` → Wheel Up
- `dial_ccw` → Wheel Down

**Modifiers:**
- `side` → Super (start menu)
- `top` → Shift
- `tall` → Alt
- `short` → Ctrl

**Navigation:**
- `dpad_up/down` → Page Up/Page Down
- `dpad_left/right` → Home/End

### Visual Feedback

- **Yellow highlight** on controller view shows selected control
- **Asterisk (*)** in window title means unsaved changes
- **"(unmapped)"** in controls list means no action assigned
- **Status bar** shows what's happening

---

## Troubleshooting

### GUI Won't Launch

**Problem:** Error when running `tourbox-gui`

**Solutions:**
1. Check that launcher script exists:
   ```bash
   ls -la /usr/local/bin/tourbox-gui
   ```
2. If missing, re-run installer or create manually:
   ```bash
   cd /path/to/tourboxelite
   ./install.sh
   ```
3. If launcher exists but still fails, check GUI dependencies:
   ```bash
   /path/to/tourboxelite/venv/bin/pip install -r tourboxelite/gui/requirements.txt
   ```
4. Verify Qt installation:
   ```bash
   /path/to/tourboxelite/venv/bin/python -c "from PySide6 import QtWidgets; print('OK')"
   ```

### Driver Won't Stop/Start

**Problem:** GUI shows error when stopping/starting driver

**Solutions:**
1. Check if driver is installed as systemd service:
   ```bash
   systemctl --user status tourbox
   ```
2. If not installed, see main README.md installation section
3. Try manual stop/start:
   ```bash
   systemctl --user stop tourbox
   systemctl --user start tourbox
   ```

### No Profiles Found

**Problem:** "No profiles found in configuration file"

**Solutions:**
1. Check config file exists:
   ```bash
   ls -la ~/.config/tourbox/mappings.conf
   ```
2. If missing, run `./install_config.sh` to create it
3. Check file permissions (should be readable)
4. Verify file has at least `[profile:default]` section

### Changes Not Saving

**Problem:** Click Save but changes don't persist

**Solutions:**
1. Check for error dialogs (file permissions, disk space)
2. Verify config file is writable:
   ```bash
   ls -la ~/.config/tourbox/mappings.conf
   ```
3. Check disk space:
   ```bash
   df -h ~
   ```
4. Look for backup files (confirms writes are working):
   ```bash
   ls -la ~/.config/tourbox/mappings.conf.backup.*
   ```

### Button Presses Don't Work in Test Mode

**Problem:** Physical button presses do nothing during Test

**Solutions:**
1. Check driver status:
   ```bash
   systemctl --user status tourbox
   ```
2. Check driver logs for errors:
   ```bash
   journalctl --user -u tourbox -n 50
   ```
3. Verify TourBox is powered on and in range
4. Try reconnecting Bluetooth:
   - Stop test
   - Turn TourBox off and on
   - Start test again
5. Check MAC address in config:
   ```bash
   grep mac_address ~/.config/tourbox/mappings.conf
   ```

### Profile Switching Not Working

**Problem:** Profile doesn't activate when switching windows

**Solutions:**
1. Check window matching rules are correct:
   - Use "Capture Active Window" feature
   - Verify app_id or window_class matches
2. Check which compositor you're using:
   ```bash
   echo $XDG_SESSION_TYPE  # Should be "wayland"
   echo $XDG_CURRENT_DESKTOP  # Shows your desktop
   ```
3. For GNOME: Install the Focused Window D-Bus extension
4. For KDE: Install `kdotool`
5. Check driver logs to see profile switching:
   ```bash
   journalctl --user -u tourbox -f
   ```
   Should show: "Switched to profile: [name]"

### Window Capture Not Working

**Problem:** "Capture Active Window" doesn't detect window

**Solutions:**
1. Make sure you're on **Wayland** (not X11):
   ```bash
   echo $XDG_SESSION_TYPE
   ```
2. Install compositor-specific tools:
   - **GNOME:** Focused Window D-Bus Extension
   - **KDE:** kdotool package
   - **Sway/Hyprland:** Built-in IPC (should work)
3. Click the target window during the 5-second countdown
4. If detection fails, manually enter window class/app_id

### GUI Freezes or Crashes

**Problem:** GUI becomes unresponsive

**Solutions:**
1. Check system resources (RAM, CPU):
   ```bash
   top
   ```
2. Kill and restart GUI:
   ```bash
   pkill -f "tourboxelite.gui"
   tourbox-gui
   ```
3. Check for Qt/Python errors in terminal output
4. Restart driver if it was left in stopped state:
   ```bash
   systemctl --user start tourbox
   ```

### Config File Corrupted

**Problem:** Can't load config, syntax errors

**Solutions:**
1. Restore from automatic backup:
   ```bash
   cd ~/.config/tourbox/
   ls -la mappings.conf.backup.*
   cp mappings.conf.backup.YYYYMMDD_HHMMSS mappings.conf
   ```
2. Or reset to defaults:
   ```bash
   ./install_config.sh
   ```
   ⚠️ WARNING: Loses all customizations!

### Getting Help

If you encounter issues not covered here:

1. **Check logs:**
   ```bash
   journalctl --user -u tourbox -n 100
   ```

2. **Enable verbose logging in GUI:**
   Edit `tourboxelite/gui/main_window.py` and change:
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Report issues:**
   - GitHub: https://github.com/your-repo/tourboxelite/issues
   - Include: OS, desktop environment, error messages, logs

---

## Appendix: Configuration File Format

The GUI reads and writes to `~/.config/tourbox/mappings.conf`.

**Example:**
```ini
[device]
mac_address = D9:BE:1E:CC:40:D7

[profile:default]
side = KEY_LEFTMETA
top = KEY_LEFTSHIFT
tall = KEY_LEFTALT
short = KEY_LEFTCTRL
scroll_up = REL_WHEEL:1
scroll_down = REL_WHEEL:-1
knob_cw = KEY_LEFTCTRL+KEY_EQUAL
knob_ccw = KEY_LEFTCTRL+KEY_MINUS
# ... etc

[profile:firefox]
app_id = firefox-esr
window_class = firefox-esr
side = KEY_LEFTCTRL+KEY_T
tall = KEY_LEFTCTRL+KEY_W
# ... etc
```

**Profile sections:**
- `[profile:name]` - Section header
- `window_class`, `app_id` - Optional matching rules
- Control mappings - One line per control

**Action formats:**
- Keyboard: `KEY_LEFTCTRL+KEY_C` (modifiers+key)
- Mouse wheel: `REL_WHEEL:1` (wheel:direction)
- Unmapped: Omit the line or set to empty

The GUI preserves comments and formatting when saving!

---

## Quick Reference Card

### Keyboard Shortcuts
- **Ctrl+S** - Save changes
- **Ctrl+T** - Test configuration
- **Arrow keys** - Navigate controls

### Workflow
1. Select profile
2. Click control
3. Configure action
4. Apply
5. Save (Ctrl+S)
6. Test (Ctrl+T)

### Action Types
- **Keyboard** - Key combos (Ctrl+C, Alt+F4, etc.)
- **Mouse Wheel** - Scroll up/down/left/right
- **None** - Disable control

### Profile Management
- **"+"** - Create new profile
- **"⚙"** - Edit profile settings
- **"-"** - Delete profile
- **Capture** - Auto-detect window info

### Testing
1. Click "Test"
2. Try physical buttons
3. Click "Stop Test"
4. Repeat as needed

---

**Enjoy your TourBox Elite with the power of a visual configuration tool!** 🎨✨

For technical details, see:
- [CONFIG_GUIDE.md](CONFIG_GUIDE.md) - Manual config editing
- [DEVELOPMENT.md](DEVELOPMENT.md) - Architecture and code
