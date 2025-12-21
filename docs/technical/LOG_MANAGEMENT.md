# TourBox Linux - Log Management

## Understanding systemd Logs

The TourBox service logs are managed by systemd's journal (journald), which handles automatic rotation and cleanup.

## Default Behavior

**Systemd journal automatically:**
- Rotates logs when they reach a certain size (typically 128MB per file)
- Limits total disk usage to 10% of filesystem or 4GB (whichever is smaller)
- Deletes old logs when limits are reached
- Compresses archived logs

**Your logs won't grow indefinitely** - systemd handles this automatically.

## Viewing Logs

### Basic Commands

```bash
# View live logs (follow mode)
journalctl --user -u tourbox -f

# View last 50 lines
journalctl --user -u tourbox -n 50

# View last 100 lines
journalctl --user -u tourbox -n 100

# View all logs for today
journalctl --user -u tourbox --since today

# View logs from last 24 hours
journalctl --user -u tourbox --since "24 hours ago"

# View logs from specific date
journalctl --user -u tourbox --since "2025-11-01"

# View logs between dates
journalctl --user -u tourbox --since "2025-11-01" --until "2025-11-02"
```

### Filtering Logs

```bash
# Show only errors and warnings
journalctl --user -u tourbox -p err

# Show only warnings and above
journalctl --user -u tourbox -p warning

# Grep for specific text
journalctl --user -u tourbox | grep "Button"

# Show logs with timestamps
journalctl --user -u tourbox -o short-precise
```

## Check Disk Usage

```bash
# See total journal disk usage
journalctl --disk-usage

# See user journal usage specifically
journalctl --user --disk-usage
```

## Manual Log Cleanup

### Clean by Time

```bash
# Delete logs older than 2 weeks
journalctl --user --vacuum-time=2weeks

# Delete logs older than 1 month
journalctl --user --vacuum-time=1month

# Delete logs older than 7 days
journalctl --user --vacuum-time=7d
```

### Clean by Size

```bash
# Keep only 100MB of logs
journalctl --user --vacuum-size=100M

# Keep only 50MB of logs
journalctl --user --vacuum-size=50M
```

### Clean by Number of Files

```bash
# Keep only 2 most recent journal files
journalctl --user --vacuum-files=2
```

## Configure Log Limits (Optional)

If you want to customize log retention, create/edit the journald config:

### System-wide Configuration

Edit `/etc/systemd/journald.conf`:

```bash
sudo nano /etc/systemd/journald.conf
```

Add or modify these settings:

```ini
[Journal]
# Maximum disk space for all logs
SystemMaxUse=500M

# Maximum disk space for runtime logs (in /run)
RuntimeMaxUse=100M

# Maximum size per journal file
SystemMaxFileSize=50M

# How long to keep old logs
MaxRetentionSec=1month

# Keep logs for 2 weeks
MaxRetentionSec=2week
```

After editing, restart journald:

```bash
sudo systemctl restart systemd-journald
```

### User Service Configuration

For user services specifically, create `~/.config/systemd/user.conf` (not commonly needed):

```ini
[Manager]
# User service logs follow system journal settings
```

## Recommended Settings for TourBox

For most users, **the defaults are fine**. The TourBox driver doesn't log excessively unless you run it with `-v` (verbose) mode.

### If you run with verbose logging often:

```bash
# Clean old logs monthly
journalctl --user --vacuum-time=1month

# Or limit to 100MB
journalctl --user --vacuum-size=100M
```

### Add to cron for automatic cleanup (optional):

```bash
# Edit crontab
crontab -e

# Add this line to clean logs older than 2 weeks every Sunday at 3am
0 3 * * 0 journalctl --user --vacuum-time=2weeks
```

## Log Verbosity Control

The TourBox service has different log levels:

### Normal Mode (Production)
```bash
systemctl --user start tourbox
# Logs: INFO level - connection status, profile switches, errors
# Typical size: ~1-2KB per day
```

### Verbose Mode (Development)
```bash
./venv/bin/python -m tourboxelite.device_ble -v
# Logs: DEBUG level - every button press, all events
# Typical size: ~100-500KB per day depending on usage
```

**Recommendation:** Only use verbose mode (`-v`) for debugging. For normal use, the service runs in INFO mode which logs minimally.

## Disable Logging (Not Recommended)

If you really don't want any logs:

```bash
# Edit service file
nano ~/.config/systemd/user/tourbox.service

# Add to [Service] section:
StandardOutput=null
StandardError=null

# Reload and restart
systemctl --user daemon-reload
systemctl --user restart tourbox
```

**Warning:** This makes debugging issues much harder!

## Export Logs

### Save current logs to file

```bash
# Save all TourBox logs to file
journalctl --user -u tourbox > tourbox-logs.txt

# Save last 1000 lines
journalctl --user -u tourbox -n 1000 > tourbox-recent.txt

# Save logs from today
journalctl --user -u tourbox --since today > tourbox-today.txt

# Save with timestamps
journalctl --user -u tourbox -o short-precise > tourbox-detailed.txt
```

### Export for bug reports

```bash
# Full logs with all metadata
journalctl --user -u tourbox -o export > tourbox-export.bin

# Or as JSON
journalctl --user -u tourbox -o json > tourbox-logs.json
```

## Monitor Log Growth

### Check log size over time

```bash
# Watch disk usage (run periodically)
watch -n 60 'journalctl --user --disk-usage'

# List journal files and sizes
ls -lh /var/log/journal/*/user-*.journal*
# or
ls -lh /run/log/journal/*/user-*.journal*
```

### Create a monitoring script

```bash
#!/bin/bash
# Save as ~/check-tourbox-logs.sh

echo "TourBox Log Statistics"
echo "====================="
echo ""

# Total log entries
TOTAL=$(journalctl --user -u tourbox | wc -l)
echo "Total log entries: $TOTAL"

# Logs from last 24h
TODAY=$(journalctl --user -u tourbox --since "24 hours ago" | wc -l)
echo "Last 24h entries: $TODAY"

# Disk usage
echo ""
echo "Disk usage:"
journalctl --user --disk-usage

# Errors and warnings
ERRORS=$(journalctl --user -u tourbox -p err --since today | wc -l)
WARNINGS=$(journalctl --user -u tourbox -p warning --since today | wc -l)
echo ""
echo "Today's errors: $ERRORS"
echo "Today's warnings: $WARNINGS"
```

Make it executable:
```bash
chmod +x ~/check-tourbox-logs.sh
./check-tourbox-logs.sh
```

## Summary

**Default behavior (recommended):**
- Systemd automatically manages log rotation
- Logs won't grow indefinitely
- No manual intervention needed

**If you want tighter control:**
- Clean old logs: `journalctl --user --vacuum-time=2weeks`
- Limit log size: `journalctl --user --vacuum-size=100M`
- Configure systemd: Edit `/etc/systemd/journald.conf`

**For development:**
- Use `-v` flag only when debugging
- Normal operation logs minimally
- Check logs with: `journalctl --user -u tourbox -f`
