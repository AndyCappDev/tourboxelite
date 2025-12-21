# TourBox Button Mapping Guide

This guide will help you map all buttons, dials, and controls on your TourBox to their hex codes.

---

## Quick Start

First, stop the TourBox service (if running) to avoid conflicts:
```bash
systemctl --user stop tourbox
```

Navigate to the tourbox directory and run the test script:
```bash
cd /path/to/tourboxelite
./venv/bin/python ble_test_tourbox.py
```

Then press each control **ONE AT A TIME** and record the hex codes you see.

When done testing, restart the service:
```bash
systemctl --user start tourbox
```

---

## Mapping Procedure

### Step 1: Buttons (Press & Release)

For each button, record BOTH the press and release codes:

| Button Name | Location | Press Code | Release Code | Notes |
|-------------|----------|------------|--------------|-------|
| **Tall** | Top-left large button | | | |
| **Short** | Top-left small button | | | |
| **Side** | Left side button | | | |
| **C1** | Right column, row 1 | | | |
| **C2** | Right column, row 1 | | | |
| **C3** | Right column, row 2 | | | |
| **C4** | Right column, row 2 | | | |
| **C5** | Right column, row 3 | | | |
| **C6** | Right column, row 3 | | | |

**Expected pattern:** Release = Press + 0x80
- Example: If press = `0x37`, then release = `0xb7`

### Step 2: Scroll Wheel

Scroll the wheel **slowly** and record what codes appear:

| Action | Observed Codes | Pattern |
|--------|----------------|---------|
| Scroll Up | | Repeated? Single? |
| Scroll Down | | Different code? |
| Click Scroll Wheel (if clickable) | | Press/Release pair? |

### Step 3: Dials (Rotary Encoders)

Turn each dial **slowly** in both directions:

| Dial Position | Turn Clockwise | Turn Counter-Clockwise | Click (if clickable) |
|---------------|----------------|------------------------|---------------------|
| **Top Dial** | | | |
| **Middle Dial** | | | |
| **Bottom Dial** | | | |

**Expected patterns:**
- Continuous codes while turning (like `0x49` repeated)
- Different codes for CW vs CCW
- Single increment per detent click

### Step 4: D-Pad

Press each direction:

| Direction | Press Code | Release Code | Notes |
|-----------|------------|--------------|-------|
| **Up** | | | |
| **Down** | | | |
| **Left** | | | |
| **Right** | | | |
| **Center (click)** | | | |

---

## Recording Your Results

### Method 1: Manual Recording

Copy this template to a new file `MY_BUTTON_MAP.md` and fill it in:

```markdown
# My TourBox Button Mapping

## Buttons
- Tall: Press=0xXX, Release=0xXX
- Short: Press=0xXX, Release=0xXX
- Side: Press=0xXX, Release=0xXX
- C1: Press=0xXX, Release=0xXX
- C2: Press=0xXX, Release=0xXX
- C3: Press=0xXX, Release=0xXX
- C4: Press=0xXX, Release=0xXX
- C5: Press=0xXX, Release=0xXX
- C6: Press=0xXX, Release=0xXX

## Scroll Wheel
- Scroll Up: 0xXX (repeated? single?)
- Scroll Down: 0xXX
- Scroll Click Press: 0xXX
- Scroll Click Release: 0xXX

## Dials
- Top Dial CW: 0xXX
- Top Dial CCW: 0xXX
- Top Dial Click Press: 0xXX
- Top Dial Click Release: 0xXX

- Middle Dial CW: 0xXX
- Middle Dial CCW: 0xXX
- Middle Dial Click Press: 0xXX
- Middle Dial Click Release: 0xXX

- Bottom Dial CW: 0xXX
- Bottom Dial CCW: 0xXX
- Bottom Dial Click Press: 0xXX
- Bottom Dial Click Release: 0xXX

## D-Pad
- Up Press: 0xXX, Release: 0xXX
- Down Press: 0xXX, Release: 0xXX
- Left Press: 0xXX, Release: 0xXX
- Right Press: 0xXX, Release: 0xXX
- Center Press: 0xXX, Release: 0xXX
```

### Method 2: Automated Logging

Modify `ble_test_tourbox.py` to log to file:

```python
def notification_handler(sender, data):
    """Handle notifications from the device"""
    global notification_count
    notification_count += 1

    msg = f"NOTIFICATION #{notification_count}: {data.hex()}"
    print(msg)

    # Also log to file
    with open("button_log.txt", "a") as f:
        f.write(msg + "\n")
```

Then review `button_log.txt` and add your own comments about which button you pressed.

---

## Example from Your Testing

From your initial test, you discovered:

| Code | Type | Notes |
|------|------|-------|
| `0x37` | Press | Unknown button A |
| `0xb7` | Release | Unknown button A |
| `0x0a` | Press | Unknown button B |
| `0x8a` | Release | Unknown button B |
| `0x49` | Active | Dial/scroll (repeated while turning) |
| `0x09` | Press | Unknown button C |
| `0x89` | Release | Unknown button C |
| `0x23` | Press | Unknown button D |
| `0xa3` | Release | Unknown button D |
| `0x22` | Press | Unknown button E |
| `0xa2` | Release | Unknown button E |

**Your task:** Figure out which physical button corresponds to each code!

---

## Tips

1. **Go slow:** Press one button, wait for output, then next button
2. **Use consistent pressure:** Some buttons might send multiple codes if pressed hard
3. **Test multiple times:** Verify each button gives consistent codes
4. **Watch for combos:** Some devices send modifier codes when multiple buttons pressed
5. **Note analog controls:** Dials and scroll wheels might send continuous position data

---

## What to Do With Results

Once you have complete mapping:

1. **Share with community:** Post to TourBoxForLinux GitHub
2. **Create input driver:** Map hex codes to Linux input events
3. **Update documentation:** Add to TOURBOX_ELITE_PROTOCOL_SOLVED.md

---

## Linux Input Event Mapping (Future)

Once you know the buttons, you'll map them like this:

```python
# Example mapping
BUTTON_MAP = {
    0x37: "BTN_0",      # Tall button
    0x0a: "BTN_1",      # Short button
    0x23: "BTN_2",      # Side button
    # ... etc
}

DIAL_MAP = {
    0x49: "REL_DIAL",   # Example: Top dial
    # ... etc
}
```

Then create a virtual input device using Python `evdev` library.

---

## Questions?

If you see unexpected behavior:
- Multiple codes for one button press
- No codes for some buttons
- Codes change between presses
- Strange patterns

Document it! This helps understand the full protocol.

---

Good luck mapping! 🎮
