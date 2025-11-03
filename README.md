# TourBox Elite Linux Driver

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Linux](https://img.shields.io/badge/platform-linux-lightgrey.svg)](https://www.linux.org/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Linux driver for the TourBox Elite - a Bluetooth Low Energy (BLE) input device by TourBox Tech Inc. This driver translates BLE input events to Linux input events via evdev/uinput.

> **⚠️ Important:** This driver is for **Bluetooth connections only**. It does **NOT** support USB connections.

## Features

- ✅ **Bluetooth LE Support** - Wireless connection via BLE
- ✅ **Full Button Mapping** - All buttons, knobs, scroll wheel, and dial supported
- ✅ **Application Profiles** - Different button mappings per application (Wayland only)
- ✅ **Systemd Integration** - Runs as a user service, starts on login
- ✅ **Easy Configuration** - Simple INI-style config file
- ✅ **Window Detection** - Automatic profile switching based on focused window (Wayland)

## Requirements

- Linux (Debian/Ubuntu tested)
- Python 3.9+
- Bluetooth support (bluez)
- Running on Wayland (for profile mode) or X11 (simple mode only)
- **For profile mode (app-specific mappings):**
  - **KDE Plasma:** `kdotool` required (see installation below)
  - **GNOME:** [Focused Window D-Bus extension](https://extensions.gnome.org/extension/5592/focused-window-d-bus/) required
  - **Sway/Hyprland:** No additional requirements

## Quick Install

> **Note:** You do NOT need to pair the TourBox Elite via Bluetooth settings. Pairing is not required and won't work. The driver connects directly to the device using its MAC address.

### Step 1: Find Your TourBox MAC Address

First, make sure your TourBox Elite is powered on and in Bluetooth mode. Do not connect with the USB cable.

Open a terminal and scan for your TourBox:

```bash
bluetoothctl devices
```

Look for a device named "TourBox Elite" in the output. The MAC address will look like `XX:XX:XX:XX:XX:XX`. Copy this address - you'll need it in Step 2 or 3.

Example output:
```
Device 12:34:56:78:9A:BC TourBox Elite
```

### Step 2: Run the Installer

```bash
git clone https://github.com/AndyCappDev/tourboxelite.git
cd tourboxelite
./install.sh
```

The installer will:
1. Create a Python virtual environment
2. Install the driver and dependencies
3. Set up your configuration file
4. Install and enable the systemd service
5. Log off and log back on again or reboot

### Step 3: Configure Your MAC Address

If you did not provide the MAC address during installation, edit the configuration file and add your TourBox MAC address:

```bash
nano ~/.config/tourbox/mappings.conf
```

Find the `[device]` section at the top of the file and set your MAC address:

```ini
[device]
mac_address = 12:34:56:78:9A:BC  # Replace with your actual MAC address
```

Save the file (Ctrl+O, Enter, Ctrl+X in nano).

You will need to log out and log back in or reboot to activate the driver after installation.

### Additional Step for KDE Plasma Users

If you're using KDE Plasma on Wayland and want profile mode (app-specific mappings), you need to install `kdotool`:

```bash
# 1. Install build dependencies
sudo apt install build-essential pkg-config libdbus-1-dev libxcb1-dev

# 2. Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
# Choose option 1 for standard installation when prompted
source $HOME/.cargo/env

# 3. Install kdotool
cargo install kdotool

# 4. Verify installation
kdotool --version
```

### Additional Step for GNOME Users

If you're using GNOME on Wayland and want profile mode (app-specific mappings), you need to install the "Focused Window D-Bus" extension:

1. Visit [Focused Window D-Bus extension page](https://extensions.gnome.org/extension/5592/focused-window-d-bus/)
2. Click the toggle switch to install
3. Verify installation:
   ```bash
   gnome-extensions list | grep focused-window-dbus
   # Should show: focused-window-dbus@flexagoon.com
   ```

Without this extension, profile mode will not work on GNOME (you can still use simple mode with a single mapping for all apps).

**Note:** Sway and Hyprland users don't need any additional software.

## Manual Installation

If you prefer manual setup:

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Install the driver
./venv/bin/pip install -e .

# 3. Find your TourBox MAC address
bluetoothctl devices
# Look for "TourBox Elite"
# NOTE: Do NOT pair the device - pairing is not required and won't work.
#       The driver connects directly using the MAC address via BLE.

# 4. Copy and edit config
mkdir -p ~/.config/tourbox
cp tourboxelite/default_mappings.conf ~/.config/tourbox/mappings.conf
nano ~/.config/tourbox/mappings.conf
# Set your MAC address in [device] section

# 5. Set up udev rules for uinput access
echo 'KERNEL=="uinput", MODE="0660", GROUP="input", OPTIONS+="static_node=uinput"' | sudo tee /etc/udev/rules.d/99-uinput.rules
sudo udevadm control --reload-rules
sudo modprobe uinput
echo "uinput" | sudo tee /etc/modules-load.d/uinput.conf

# 6. Add user to input group (required for device access)
sudo usermod -a -G input $USER
# You'll need to log out and back in for this to take effect

# 7. Set up systemd service
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/tourbox.service
# Add the following content (replace /path/to/tourboxelite with actual path):
#
# [Unit]
# Description=TourBox Elite Driver
# After=graphical-session.target
#
# [Service]
# Type=simple
# ExecStart=/path/to/tourboxelite/venv/bin/python -m tourboxelite.device_ble
# Restart=on-failure
# RestartSec=5
#
# [Install]
# WantedBy=default.target

# 8. Enable and start service
systemctl --user daemon-reload
systemctl --user enable tourbox
systemctl --user start tourbox
```

## Configuration

Edit `~/.config/tourbox/mappings.conf` to customize button mappings.

The config uses **profiles** - the `[profile:default]` section is required and contains your main button mappings:

```ini
[device]
mac_address = XX:XX:XX:XX:XX:XX

[profile:default]
# Button mappings
side = KEY_LEFTMETA
top = KEY_LEFTSHIFT
tall = KEY_LEFTALT
# ... more buttons

# Rotary controls
scroll_up = REL_WHEEL:1
scroll_down = REL_WHEEL:-1
knob_cw = KEY_LEFTCTRL+KEY_EQUAL    # Zoom in
knob_ccw = KEY_LEFTCTRL+KEY_MINUS   # Zoom out
# ... more rotary controls
```

### App-Specific Profiles (Wayland only)

On Wayland, you can add app-specific profiles that automatically switch when you focus different windows:

```ini
[profile:vscode]
window_class = Code
side = KEY_LEFTCTRL+KEY_SPACE          # Code completion
knob_cw = KEY_LEFTCTRL+KEY_EQUAL       # Zoom in
dpad_left = KEY_LEFTCTRL+KEY_PAGEUP    # Previous tab
dpad_right = KEY_LEFTCTRL+KEY_PAGEDOWN # Next tab
# ... all other buttons

[profile:firefox]
window_class = firefox-esr
side = KEY_LEFTALT+KEY_LEFT     # Back
top = KEY_LEFTALT+KEY_RIGHT     # Forward
knob_cw = KEY_LEFTCTRL+KEY_EQUAL    # Zoom in
# ... all other buttons
```

**Note:** On X11, only `[profile:default]` is used. App-specific profiles require Wayland.

After editing, restart the service:
```bash
systemctl --user restart tourbox
```

## Usage

### Service Management

```bash
# Start the driver
systemctl --user start tourbox

# Stop the driver
systemctl --user stop tourbox

# Check status
systemctl --user status tourbox

# View logs
journalctl --user -u tourbox -f

# Restart after config changes
systemctl --user restart tourbox
```

### Manual Testing

Before running the driver manually, you must stop the systemd service first (otherwise it will conflict with the manual instance):

```bash
# Stop the service
systemctl --user stop tourbox

# Navigate to the tourboxelite directory
cd /path/to/tourboxelite

# Run directly in terminal with verbose logging
./venv/bin/python -m tourboxelite.device_ble -v
```

Press `Ctrl+C` to stop.

When you're done testing, restart the service:

```bash
systemctl --user start tourbox
```

## Uninstall

```bash
./uninstall.sh
```

Or manually:

```bash
systemctl --user stop tourbox
systemctl --user disable tourbox
rm ~/.config/systemd/user/tourbox.service
rm -rf ~/.config/tourbox
systemctl --user daemon-reload
```

## Troubleshooting

### Service won't start

Check logs:
```bash
journalctl --user -u tourbox -n 50
```

Common issues:
- MAC address not set in config
- TourBox not powered on or out of range
- Missing Python dependencies
- Device already connected to another system

### "/dev/uinput" cannot be opened for writing

If you see this error in the logs, the uinput device permissions aren't set correctly. The install script should handle this automatically, but if needed, fix it manually:

```bash
# Create udev rule
echo 'KERNEL=="uinput", MODE="0660", GROUP="input", OPTIONS+="static_node=uinput"' | sudo tee /etc/udev/rules.d/99-uinput.rules

# Reload udev and load module
sudo udevadm control --reload-rules
sudo modprobe uinput

# Ensure module loads on boot
echo "uinput" | sudo tee /etc/modules-load.d/uinput.conf

# Verify permissions
ls -l /dev/uinput
# Should show: crw-rw---- 1 root input
```

### Profile switching not working

Profile mode requires Wayland. Verify:
```bash
echo $XDG_SESSION_TYPE
# Should output: wayland
```

Test window detection:
```bash
./venv/bin/python -m tourboxelite.window_monitor
```

### Buttons not responding

Make sure you're a member of the `input` group:
```bash
sudo usermod -a -G input $USER
# Log out and back in
```

## Documentation

- [Detailed configuration guide](docs/CONFIG_GUIDE.md)
- [Example configurations](tourboxelite/default_mappings.conf)
- [Development guide](docs/DEVELOPMENT.md)

## License

MIT License - See [LICENSE.txt](LICENSE.txt) file

