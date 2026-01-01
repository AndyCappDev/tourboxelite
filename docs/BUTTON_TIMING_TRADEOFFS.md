# Understanding Button Behavior in TourBox Linux

## Immediate Fire (Default Behavior)

The TourBox Linux driver uses **immediate fire** - base actions fire instantly when you press a button, with **zero latency**. This mimics the feel of a physical keyboard.

### How Double-Press Works

When you configure a double-press action on a button:

1. **First press** → Base action fires immediately (no delay!)
2. **First release** → Base action releases
3. **Second press within timeout** → Double-press action fires
4. **Second release** → Double-press action releases

**Example:** Button with Space (pan) + double-press Shift:
- Quick tap → Space tap
- Hold → Space held (pan works!)
- Double-tap → Space tap, then Shift

The "dirty" part: If you double-press, you get a quick tap of the base action before the double-press action. For most workflows, this is acceptable and preferable to having latency on every press.

### Double-Press Timeout

The timeout (default 300ms) determines how quickly you must tap twice:
- **100-150ms**: Very tight, requires fast fingers
- **200-250ms**: Good balance for experienced users
- **300ms** (default): Safe default, reliable double-press detection
- **400-500ms**: More forgiving, easier to hit double-press

Adjust this in Profile Settings → Double-Click → Timeout.

---

## Activate on Release (Clean Combos)

For buttons where you need **clean combos** (no base action before combo fires), enable "Activate on Release":

- Base action deferred until button release, then fires **immediately** as tap
- Combos fire cleanly without base action interference
- Double-press uses dirty input (base fires on release, double-press on second press)

**Use this for:**
- Buttons with many combos that shouldn't fire the base action first
- Tool switching where you need clean combo behavior

**Don't use this for:**
- Hold actions like pan/zoom (they need key to stay down while held)

---

## Why This Works Differently Than Windows

The official TourBox driver on Windows:
- Communicates directly with applications via Windows APIs
- Can use overlay menus and application-specific hooks
- Has deeper system integration that allows "smart" behavior

The Linux driver:
- Emulates a standard keyboard/mouse input device (via uinput)
- Sends keystrokes just like a physical keyboard would
- Works within keyboard emulation constraints

---

## Quick Reference

| Scenario | Default (Immediate Fire) | Activate on Release |
|----------|-------------------------|---------------------|
| Base action timing | Instant on press | Instant on release (as tap) |
| Hold behavior | Works (key stays down) | Broken (fires as tap) |
| Double-press | Quick base tap, then double action | Quick base tap on release, then double |
| Combos | Base may fire briefly first | Clean (no base before combo) |
| Best for | Pan/zoom, modifiers | Buttons with many combos |

---

## See Also

- **[Why No Overlay Features?](WHY_NO_OVERLAYS.md)** - More details on Linux driver architecture and limitations.
