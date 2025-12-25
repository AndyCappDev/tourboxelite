# Why TourBox Linux Doesn't Have Overlay Features

## Features That Won't Be Implemented

- **TourMenu**: Popup context menus triggered by TourBox buttons, navigable with scroll/dial
- **HUD**: On-screen display showing current button mappings with press highlighting

These are features that exist in the official TourBox software for Windows/Mac.

## The Problem: Linux Desktop Fragmentation

Creating overlay windows (transparent, always-on-top, click-through) requires different implementations for different Linux desktop environments.

### X11

Works fine. Traditional X11 window hints handle overlays without issues.

### Wayland

Wayland's security model intentionally restricts applications from:
- Positioning windows arbitrarily on screen
- Creating always-on-top windows
- Making click-through transparent surfaces

Each compositor has its own solution (or lack thereof):

| Desktop | Overlay Solution | Notes |
|---------|------------------|-------|
| Sway, Hyprland (wlroots) | `wlr-layer-shell` protocol | Works, but requires GTK + gtk-layer-shell |
| KDE Plasma | Partial Qt support | May work, not guaranteed |
| GNOME | GNOME Shell extension only | Completely separate JavaScript codebase |

### What This Means

To properly support overlays across Linux desktops, this project would need **three separate implementations**:

1. **Qt-based** for X11 and KDE Wayland
2. **GTK + gtk-layer-shell** for wlroots compositors (Sway, Hyprland)
3. **GNOME Shell extension** (JavaScript) for GNOME Wayland

Each implementation would need to:
- Be written and maintained separately
- Communicate with the driver via different IPC mechanisms
- Handle compositor-specific quirks
- Be tested across multiple desktop versions

## The Verdict

The core driver functionality (button mapping, key simulation, profile switching) works everywhere. Adding overlay features would:

- Triple the GUI-related codebase
- Add significant maintenance burden
- Still leave some users without support
- Delay other improvements

This is likely why TourBox themselves haven't released an official Linux driver—the fragmentation makes feature parity impractical.

## Alternatives

If you want overlay-like functionality:

- **Context menu navigation**: Use modifier buttons to navigate native application context menus entirely from your TourBox. Set up a button (e.g., C1) as a modifier with Right Click as its base action, then map `C1 + scroll_up` to Up Arrow and `C1 + scroll_down` to Down Arrow. Hold C1 to open the context menu, scroll to navigate, release and press another button for Enter/Left Click to select. This recreates much of the TourMenu workflow using existing app menus. See the [GUI User Guide](GUI_USER_GUIDE.md#common-modifier-patterns) for details.
- **Keyboard shortcut reference**: Use your desktop's built-in shortcut overlay (KDE: hold Super key, GNOME: similar)
- **Cheat sheet**: Keep a reference image/document open on a second monitor
- **Desktop widgets**: Some desktops support custom widgets that could display mappings

## Future

If Wayland compositors converge on a standard overlay protocol that GNOME adopts, this decision could be revisited. Until then, the focus will remain on the core driver and configuration GUI.
