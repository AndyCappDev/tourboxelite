"""Update checker for TourBox Elite GUI

Fetches version information from GitHub and compares with installed version.
"""

import re
import logging
import urllib.request
import urllib.error

from PySide6.QtCore import QThread, Signal

from tourboxelite import VERSION

logger = logging.getLogger(__name__)

# URL to fetch VERSION from GitHub
VERSION_URL = "https://raw.githubusercontent.com/AndyCappDev/tourboxelite/master/tourboxelite/__init__.py"
REQUEST_TIMEOUT = 5  # seconds


class UpdateChecker(QThread):
    """Background thread to check for updates on GitHub"""

    # Signals
    update_available = Signal(str, str)  # (latest_version, current_version)
    no_update = Signal(str)              # (current_version)
    check_failed = Signal(str)           # (error_message)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_version = VERSION

    def run(self):
        """Execute update check in background thread"""
        try:
            logger.info(f"Checking for updates (current version: {self.current_version})")

            # Fetch __init__.py from GitHub
            request = urllib.request.Request(
                VERSION_URL,
                headers={'User-Agent': f'TourBoxElite/{self.current_version}'}
            )
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                content = response.read().decode('utf-8')

            # Parse VERSION from content
            latest_version = self._parse_version(content)
            if not latest_version:
                self.check_failed.emit("Could not parse version from GitHub")
                return

            logger.info(f"Latest version on GitHub: {latest_version}")

            # Compare versions
            if self._is_newer(latest_version, self.current_version):
                logger.info(f"Update available: {latest_version}")
                self.update_available.emit(latest_version, self.current_version)
            else:
                logger.info("Already running latest version")
                self.no_update.emit(self.current_version)

        except urllib.error.URLError as e:
            error_msg = f"Network error: {e.reason}"
            logger.error(error_msg)
            self.check_failed.emit(error_msg)
        except TimeoutError:
            error_msg = "Request timed out"
            logger.error(error_msg)
            self.check_failed.emit(error_msg)
        except Exception as e:
            error_msg = f"Error checking for updates: {e}"
            logger.error(error_msg, exc_info=True)
            self.check_failed.emit(error_msg)

    def _parse_version(self, content: str) -> str:
        """Parse VERSION string from __init__.py content

        Args:
            content: File content

        Returns:
            Version string or None if not found
        """
        match = re.search(r"VERSION\s*=\s*['\"]([^'\"]+)['\"]", content)
        if match:
            return match.group(1)
        return None

    def _is_newer(self, latest: str, current: str) -> bool:
        """Compare semantic versions

        Args:
            latest: Latest version string (e.g., '2.2.0')
            current: Current version string (e.g., '2.1.0')

        Returns:
            True if latest is newer than current
        """
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            return latest_parts > current_parts
        except ValueError:
            # If parsing fails, treat as no update
            logger.warning(f"Could not parse versions: {latest} vs {current}")
            return False
