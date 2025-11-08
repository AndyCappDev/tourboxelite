#!/usr/bin/env python3
"""Main window for TourBox Elite Configuration GUI"""

import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSplitter, QMessageBox, QDialog, QProgressDialog, QToolBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence, QIcon

# Import from GUI modules
from .profile_manager import ProfileManager
from .controls_list import ControlsList
from .controller_view import ControllerView
from .driver_manager import DriverManager
from .control_editor import ControlEditor
from .config_writer import (save_profile, save_profile_metadata, create_new_profile,
                            profile_exists_in_config, cleanup_old_backups)

# Import from existing driver code
from tourboxelite.config_loader import load_profiles

logger = logging.getLogger(__name__)


class TourBoxConfigWindow(QMainWindow):
    """Main configuration window for TourBox Elite"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TourBox Elite Configuration")
        self.setMinimumSize(1000, 700)
        self.resize(1280, 1024)
        self.driver_was_running = False

        # Set window icon
        self._set_window_icon()

        # Track current profile and modifications
        self.current_profile = None
        self.modified_mappings = {}  # control_name -> action_string
        self.is_modified = False
        self.is_testing = False  # Track if we're in testing mode
        self.profile_original_names = {}  # Track original names of profiles (for renames)

        # Create menu bar
        self._create_menu_bar()

        # Create toolbar
        self._create_toolbar()

        # Ensure status bar is created and visible
        self.statusBar().setVisible(True)
        self.statusBar().showMessage("Initializing...")

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create main splitter (left side | right side)
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)

        # Left side container
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Top left: Controller image
        self.controller_view = ControllerView()
        self.controller_view.setMinimumSize(400, 225)
        left_layout.addWidget(self.controller_view, stretch=1)

        # Bottom left: Profiles manager
        self.profile_manager = ProfileManager()
        self.profile_manager.setMinimumSize(400, 450)
        self.profile_manager.profile_selected.connect(self._on_profile_selected)
        self.profile_manager.profiles_changed.connect(self._on_profiles_changed)
        self.profile_manager.profiles_reset.connect(self._on_profiles_reset)
        left_layout.addWidget(self.profile_manager, stretch=0)

        main_splitter.addWidget(left_widget)

        # Right side container
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Top right: Controls list
        self.controls_list = ControlsList()
        self.controls_list.setMinimumSize(400, 300)
        self.controls_list.control_selected.connect(self._on_control_selected)
        right_layout.addWidget(self.controls_list, stretch=1)

        # Bottom right: Control editor
        self.control_editor = ControlEditor()
        self.control_editor.setMinimumSize(400, 200)
        self.control_editor.action_changed.connect(self._on_action_changed)
        right_layout.addWidget(self.control_editor, stretch=0)

        main_splitter.addWidget(right_widget)

        # Set initial splitter sizes (40% left, 60% right)
        main_splitter.setSizes([400, 600])

        logger.info("Main window initialized (initialization deferred)")

    def _create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Save action
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.setStatusTip("Save profile changes to configuration file")
        self.save_action.triggered.connect(self._on_save)
        self.save_action.setEnabled(False)
        file_menu.addAction(self.save_action)

        # Test action
        self.test_action = QAction("&Test", self)
        self.test_action.setShortcut(QKeySequence("Ctrl+T"))
        self.test_action.setStatusTip("Start test mode - save and start driver to test with physical device")
        self.test_action.triggered.connect(self._on_test)
        self.test_action.setEnabled(False)
        file_menu.addAction(self.test_action)

        file_menu.addSeparator()

        # Quit action
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.setStatusTip("Quit application")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def _create_toolbar(self):
        """Create the toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Add save button
        toolbar.addAction(self.save_action)

        # Add test button
        toolbar.addAction(self.test_action)

    def _set_window_icon(self):
        """Set the window icon from assets"""
        import os
        from pathlib import Path

        # Get the path to the icon file
        # __file__ is the path to this module (main_window.py)
        assets_dir = Path(__file__).parent / "assets"
        icon_path = assets_dir / "tourbox-icon.png"

        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self.setWindowIcon(icon)
            logger.debug(f"Window icon set from {icon_path}")
        else:
            logger.warning(f"Icon file not found: {icon_path}")

    def showEvent(self, event):
        """Called when window is shown - perform initialization"""
        super().showEvent(event)

        # Only run initialization once
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        # Use QTimer to ensure window is fully rendered before showing dialog
        QTimer.singleShot(100, self._perform_initialization)

    def _perform_initialization(self):
        """Perform initialization steps with visual feedback"""
        # Create progress dialog
        self.progress = QProgressDialog(
            "Initializing...",
            None,  # No cancel button
            0, 0,  # Indeterminate progress (min=0, max=0)
            self
        )
        self.progress.setWindowTitle("Initializing TourBox Configuration")
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setMinimumDuration(0)  # Show immediately
        self.progress.setAutoClose(False)  # Don't auto-close
        self.progress.setAutoReset(False)  # Don't auto-reset
        self.progress.setValue(0)
        self.progress.show()

        # Force the dialog to paint by processing events
        QApplication.processEvents()

        # Defer the actual work to allow dialog to fully render
        QTimer.singleShot(50, self._check_driver_status)

    def _check_driver_status(self):
        """Step 1: Check driver status"""
        self.progress.setLabelText("Checking driver status...")
        QApplication.processEvents()

        # Small delay to ensure message is visible
        QTimer.singleShot(100, self._stop_driver_step)

    def _stop_driver_step(self):
        """Step 2: Stop driver"""
        self.progress.setLabelText("Stopping TourBox driver service...")
        QApplication.processEvents()

        self._stop_driver()

        # Continue to next step
        QTimer.singleShot(50, self._load_profiles_step)

    def _load_profiles_step(self):
        """Step 3: Load profiles"""
        self.progress.setLabelText("Loading configuration...")
        QApplication.processEvents()

        self._load_profiles()

        # Finish initialization
        QTimer.singleShot(50, self._finish_initialization)

    def _finish_initialization(self):
        """Step 4: Finish and close dialog"""
        # Close progress dialog
        self.progress.close()

        # Update status bar with driver status
        if self.driver_was_running:
            self.statusBar().showMessage("Ready - Driver stopped (GUI has exclusive access)")
        else:
            self.statusBar().showMessage("Ready - Driver was not running")

        logger.info("Initialization complete")

    def _stop_driver(self):
        """Stop the TourBox driver service"""
        # Check if driver is running
        self.driver_was_running = DriverManager.is_running()

        if not self.driver_was_running:
            logger.info("Driver is not running, no need to stop")
            return

        logger.info("Stopping driver...")

        success, message = DriverManager.stop_driver()

        if success:
            logger.info("Driver stopped successfully")
        else:
            logger.error(f"Failed to stop driver: {message}")
            QMessageBox.warning(
                self,
                "Driver Stop Failed",
                f"Failed to stop the TourBox driver:\n{message}\n\n"
                "The GUI may not be able to connect to the device."
            )

    def _load_profiles(self):
        """Load profiles from configuration file"""
        try:
            profiles = load_profiles()

            if not profiles:
                QMessageBox.warning(
                    self,
                    "No Profiles Found",
                    "No profiles found in configuration file.\n"
                    "Please check your configuration at ~/.config/tourbox/mappings.conf"
                )
                self.statusBar().showMessage("No profiles found")
                return

            # Track original names of all loaded profiles (for detecting renames)
            # Use id(profile) as key since Profile objects aren't hashable
            self.profile_original_names = {id(profile): profile.name for profile in profiles}

            # Load profiles into UI
            self.profile_manager.load_profiles(profiles)
            self.statusBar().showMessage(f"Loaded {len(profiles)} profile(s)")

            logger.info(f"Loaded {len(profiles)} profiles from config")

        except Exception as e:
            error_msg = f"Error loading profiles: {e}"
            logger.error(error_msg, exc_info=True)
            QMessageBox.critical(
                self,
                "Error Loading Profiles",
                f"Failed to load configuration:\n{e}"
            )
            self.statusBar().showMessage("Error loading profiles")

    def _on_profile_selected(self, profile):
        """Handle profile selection

        Args:
            profile: Selected Profile object
        """
        logger.info(f"Profile selected: {profile.name}")

        # Check if there are unsaved changes (profile settings OR control mappings)
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Profile '{self.current_profile.name}' has unsaved changes.\n\n"
                "Do you want to save them before switching profiles?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )

            if reply == QMessageBox.Save:
                # Save the changes (both profile metadata and control mappings)
                # Get the original name (before any renames) to check if profile exists
                original_name = self.profile_original_names.get(id(self.current_profile), self.current_profile.name)
                profile_exists = profile_exists_in_config(original_name)

                if not profile_exists:
                    # This is a new profile - create it
                    logger.info(f"Creating new profile: {self.current_profile.name}")
                    success = create_new_profile(self.current_profile)
                    # Update the original name tracker for the newly created profile
                    if success:
                        self.profile_original_names[id(self.current_profile)] = self.current_profile.name
                else:
                    # Existing profile - save metadata and mappings
                    # Determine if profile was renamed
                    old_name = original_name if original_name != self.current_profile.name else None

                    metadata_success = save_profile_metadata(self.current_profile, old_name)
                    # Update the original name tracker if profile was renamed
                    if old_name and metadata_success:
                        self.profile_original_names[id(self.current_profile)] = self.current_profile.name

                    mappings_success = True
                    if self.modified_mappings:
                        mappings_success = save_profile(self.current_profile, self.modified_mappings)
                    success = metadata_success and mappings_success

                if not success:
                    QMessageBox.critical(
                        self,
                        "Save Failed",
                        "Failed to save changes. Profile switch cancelled."
                    )
                    # Reselect the current profile
                    self.profile_manager.reselect_current_profile()
                    return
                cleanup_old_backups()
            elif reply == QMessageBox.Cancel:
                # Cancel the profile switch - reselect current profile
                self.profile_manager.reselect_current_profile()
                return
            elif reply == QMessageBox.Discard:
                # Discard changes and reload profile list to revert display
                logger.info(f"Discarding changes to {self.current_profile.name}")

                # IMPORTANT: Clear modifications FIRST before reloading profiles
                # to prevent infinite loop (reload triggers profile_selected signal)
                self.modified_mappings = {}
                self.is_modified = False

                # Reload the current profile to revert UI changes before switching
                self.controls_list.load_profile(self.current_profile)
                # Also need to reload profile list to revert any name/window matching changes
                from tourboxelite.config_loader import load_profiles
                profiles = load_profiles()
                # Reset original names tracking
                self.profile_original_names = {id(profile): profile.name for profile in profiles}
                self.profile_manager.load_profiles(profiles)

        # Store current profile and reset modifications
        self.current_profile = profile
        self.modified_mappings = {}
        self.is_modified = False
        self._update_window_title()

        # Disable Save button, but enable Test button (can test saved config)
        self.save_action.setEnabled(False)
        self.test_action.setEnabled(True)

        self.statusBar().showMessage(f"Profile: {profile.name}")

        # Clear any highlighted control from previous profile
        self.controller_view.clear_highlight()

        # Load profile's controls into controls list (loads from saved data)
        self.controls_list.load_profile(profile)

        # Disable control editor until a control is selected
        self.control_editor.setEnabled(False)

    def _on_profiles_changed(self):
        """Handle profile metadata changes (name, window matching rules)"""
        logger.info("Profile settings changed")

        # Mark as modified (profile settings changed, need to save to config)
        self.is_modified = True
        self._update_window_title()

        # Enable save button
        self.save_action.setEnabled(True)

        self.statusBar().showMessage(f"Profile '{self.current_profile.name}' settings modified (not saved)")

    def _on_profiles_reset(self, profile):
        """Handle profiles reset (reload from config without unsaved changes check)

        This is called when deleting an unsaved profile to reset everything
        to the saved state without prompting for unsaved changes.

        Args:
            profile: Profile to switch to
        """
        logger.info(f"Profiles reset, switching to: {profile.name}")

        # Clear modifications and switch profile
        self.current_profile = profile
        self.modified_mappings = {}
        self.is_modified = False
        self._update_window_title()

        # Disable Save button, enable Test button
        self.save_action.setEnabled(False)
        self.test_action.setEnabled(True)

        self.statusBar().showMessage(f"Profile: {profile.name}")

        # Clear any highlighted control
        self.controller_view.clear_highlight()

        # Load profile's controls
        self.controls_list.load_profile(profile)

        # Disable control editor until a control is selected
        self.control_editor.setEnabled(False)

    def _on_control_selected(self, control_name: str):
        """Handle control selection from list

        Args:
            control_name: Name of selected control
        """
        logger.info(f"Control selected: {control_name}")

        # Highlight in controller view
        self.controller_view.highlight_control(control_name)

        # Get current action from controls list table
        # Find the row for this control
        current_action = "(unmapped)"
        for row in range(self.controls_list.table.rowCount()):
            item = self.controls_list.table.item(row, 0)
            if item and item.data(Qt.UserRole) == control_name:
                action_item = self.controls_list.table.item(row, 1)
                if action_item:
                    current_action = action_item.text()
                break

        # Load into editor
        self.control_editor.load_control(control_name, current_action)

        # Update status bar
        self.statusBar().showMessage(f"Editing: {control_name}")

    def _on_action_changed(self, control_name: str, action_str: str):
        """Handle action change from editor

        Args:
            control_name: Name of the control
            action_str: New action string
        """
        logger.info(f"Action changed: {control_name} -> {action_str}")

        # Track the modification
        self.modified_mappings[control_name] = action_str
        self.is_modified = True
        self._update_window_title()

        # Enable Save and Test buttons
        self.save_action.setEnabled(True)
        self.test_action.setEnabled(True)

        # Convert action string to human-readable format
        readable_action = self._action_to_readable(action_str)

        # Update the controls list display
        for row in range(self.controls_list.table.rowCount()):
            item = self.controls_list.table.item(row, 0)
            if item and item.data(Qt.UserRole) == control_name:
                action_item = self.controls_list.table.item(row, 1)
                if action_item:
                    action_item.setText(readable_action)
                break

        self.statusBar().showMessage(f"Modified: {control_name} (not saved)")

    def _update_window_title(self):
        """Update window title to show modified state"""
        title = "TourBox Elite Configuration"
        if self.current_profile:
            title += f" - {self.current_profile.name}"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)

    def _on_save(self):
        """Handle Save action - save profile changes to config file"""
        if not self.current_profile:
            QMessageBox.warning(self, "No Profile", "No profile is currently selected.")
            return

        if not self.is_modified:
            QMessageBox.information(self, "No Changes", "No changes to save.")
            return

        logger.info(f"Saving profile: {self.current_profile.name}")
        logger.debug(f"Modified mappings: {self.modified_mappings}")

        # Get the original name (before any renames) to check if profile exists
        original_name = self.profile_original_names.get(id(self.current_profile), self.current_profile.name)
        profile_exists = profile_exists_in_config(original_name)

        if not profile_exists:
            # This is a new profile - create it
            logger.info(f"Creating new profile: {self.current_profile.name}")
            success = create_new_profile(self.current_profile)
            if not success:
                self.statusBar().showMessage("Failed to create new profile")
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    f"Failed to create new profile '{self.current_profile.name}'.\n\n"
                    "Check the logs for details."
                )
                return
            # Update the original name tracker for the newly created profile
            self.profile_original_names[id(self.current_profile)] = self.current_profile.name
        else:
            # Existing profile - save metadata and mappings
            # Determine if profile was renamed
            old_name = original_name if original_name != self.current_profile.name else None

            # Save profile metadata first (name, window matching)
            metadata_success = save_profile_metadata(self.current_profile, old_name)
            if not metadata_success:
                self.statusBar().showMessage("Failed to save profile metadata")
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    f"Failed to save profile metadata for '{self.current_profile.name}'.\n\n"
                    "Check the logs for details."
                )
                return

            # Update the original name tracker if profile was renamed
            if old_name:
                self.profile_original_names[id(self.current_profile)] = self.current_profile.name

            # Save the control mappings if any were modified
            mappings_success = True
            if self.modified_mappings:
                mappings_success = save_profile(self.current_profile, self.modified_mappings)

            success = metadata_success and mappings_success

        if success:
            # Clear modified state
            self.modified_mappings = {}
            self.is_modified = False
            self._update_window_title()

            # Disable Save button, keep Test enabled
            self.save_action.setEnabled(False)
            self.test_action.setEnabled(True)

            # Clean up old backups
            cleanup_old_backups()

            self.statusBar().showMessage("Profile saved successfully")
            QMessageBox.information(
                self,
                "Save Successful",
                f"Profile '{self.current_profile.name}' has been saved.\n\n"
                "Use Test to restart the driver and try your changes."
            )
        else:
            self.statusBar().showMessage("Failed to save profile")
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save profile '{self.current_profile.name}'.\n\n"
                "Check the logs for details."
            )

    def _on_test(self):
        """Handle Test/Stop Test action - toggle between testing and editing mode"""
        if self.is_testing:
            # Currently testing - stop the driver
            self._stop_testing()
        else:
            # Currently editing - start testing
            self._start_testing()

    def _start_testing(self):
        """Start testing mode - save, start driver, disable UI"""
        if not self.current_profile:
            QMessageBox.warning(self, "No Profile", "No profile is currently selected.")
            return

        # Save first if there are modifications (mappings or profile metadata)
        if self.is_modified:
            logger.info("Saving before test...")

            # Check if profile exists in config (could be new, unsaved profile)
            from .config_writer import profile_exists_in_config
            original_name = self.profile_original_names.get(id(self.current_profile), self.current_profile.name)
            profile_exists = profile_exists_in_config(original_name)

            if not profile_exists:
                # This is a new profile - create it
                logger.info(f"Creating new profile before test: {self.current_profile.name}")
                success = create_new_profile(self.current_profile)
                # Update the original name tracker for the newly created profile
                if success:
                    self.profile_original_names[id(self.current_profile)] = self.current_profile.name
            else:
                # Existing profile - save metadata and mappings
                # Determine if profile was renamed
                old_name = original_name if original_name != self.current_profile.name else None

                # Save profile metadata (name, window matching)
                metadata_success = save_profile_metadata(self.current_profile, old_name)
                # Update the original name tracker if profile was renamed
                if old_name and metadata_success:
                    self.profile_original_names[id(self.current_profile)] = self.current_profile.name

                # Save control mappings
                mappings_success = True
                if self.modified_mappings:
                    mappings_success = save_profile(self.current_profile, self.modified_mappings)

                success = metadata_success and mappings_success

            if not success:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    "Failed to save changes. Cannot test without saving."
                )
                return

            # Reload profiles from config to sync in-memory state with saved state
            logger.info("Reloading profiles from config after save...")
            current_profile_name = self.current_profile.name  # Remember which profile we're testing
            profiles = load_profiles()

            # Update the profile_original_names tracking
            self.profile_original_names = {id(profile): profile.name for profile in profiles}

            # Find the current profile in the reloaded list
            for profile in profiles:
                if profile.name == current_profile_name:
                    self.current_profile = profile
                    break

            # Update profile manager's profiles list
            self.profile_manager.profiles = profiles

            # Manually update profile manager's current profile and reselect
            self.profile_manager.current_profile = self.current_profile
            self.profile_manager._reload_profile_list()

            # Reload controls list to show saved values
            self.controls_list.load_profile(self.current_profile)

            # Clear modified state
            self.modified_mappings = {}
            self.is_modified = False
            self._update_window_title()
            self.save_action.setEnabled(False)

            # Clean up old backups
            cleanup_old_backups()

        # Show progress dialog
        logger.info("Starting driver for testing...")
        progress = QProgressDialog("Starting TourBox driver for testing...", None, 0, 0, self)
        progress.setWindowTitle("Starting Test Mode")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()

        success, message = DriverManager.start_driver()

        progress.close()

        if success:
            logger.info("Driver started successfully - entering test mode")

            # Enter testing mode
            self.is_testing = True

            # Disable entire UI
            self._set_ui_enabled(False)

            # Change Test button to Stop Test and keep it enabled
            self.test_action.setText("Stop Test")
            self.test_action.setEnabled(True)

            self.statusBar().showMessage("Testing mode - Driver running. Click 'Stop Test' when done.")

            QMessageBox.information(
                self,
                "Test Mode Active",
                "Driver is now running.\n\n"
                "Test your button mappings with the physical TourBox device.\n\n"
                "Click 'Stop Test' when you're done to continue editing."
            )
        else:
            logger.error(f"Failed to start driver: {message}")
            self.statusBar().showMessage("Failed to start driver")
            QMessageBox.critical(
                self,
                "Start Failed",
                f"Failed to start driver:\n{message}\n\n"
                "You may need to start it manually:\n"
                "  systemctl --user start tourbox"
            )

    def _stop_testing(self):
        """Stop testing mode - stop driver, re-enable UI"""
        # Show progress dialog
        logger.info("Stopping driver...")
        progress = QProgressDialog("Stopping TourBox driver...", None, 0, 0, self)
        progress.setWindowTitle("Stopping Test Mode")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()

        success, message = DriverManager.stop_driver()

        progress.close()

        if success:
            logger.info("Driver stopped successfully - exiting test mode")

            # Exit testing mode
            self.is_testing = False

            # Re-enable UI
            self._set_ui_enabled(True)

            # Change button back to Test and keep it enabled
            self.test_action.setText("Test")
            self.test_action.setEnabled(True)

            self.statusBar().showMessage("Ready - Driver stopped (GUI has exclusive access)")
        else:
            logger.error(f"Failed to stop driver: {message}")
            self.statusBar().showMessage("Failed to stop driver")
            QMessageBox.critical(
                self,
                "Stop Failed",
                f"Failed to stop driver:\n{message}\n\n"
                "You may need to stop it manually:\n"
                "  systemctl --user stop tourbox"
            )

    def _set_ui_enabled(self, enabled: bool):
        """Enable or disable the entire UI (for testing mode)

        Args:
            enabled: True to enable UI, False to disable
        """
        # Disable/enable main components
        self.profile_manager.setEnabled(enabled)
        self.controls_list.setEnabled(enabled)
        self.controller_view.setEnabled(enabled)
        self.control_editor.setEnabled(enabled)

        # Disable/enable Save action only if we have modifications
        if enabled:
            self.save_action.setEnabled(self.is_modified)
        else:
            self.save_action.setEnabled(False)

    def _action_to_readable(self, action_str: str) -> str:
        """Convert action string to human-readable format

        Args:
            action_str: Action string like 'KEY_LEFTCTRL+KEY_C'

        Returns:
            Human-readable string like 'Ctrl+C'
        """
        if not action_str or action_str == "none" or action_str == "(none)":
            return "(unmapped)"

        # Handle mouse wheel
        if action_str.startswith("REL_WHEEL:"):
            value = action_str.split(":")[1]
            return f"Wheel {'Up' if int(value) > 0 else 'Down'}"
        if action_str.startswith("REL_HWHEEL:"):
            value = action_str.split(":")[1]
            return f"Wheel {'Right' if int(value) > 0 else 'Left'}"

        # Symbol key mapping
        SYMBOL_MAP = {
            'LEFTBRACE': '[',
            'RIGHTBRACE': ']',
            'SEMICOLON': ';',
            'APOSTROPHE': "'",
            'GRAVE': '`',
            'BACKSLASH': '\\',
            'COMMA': ',',
            'DOT': '.',
            'SLASH': '/',
            'MINUS': '-',
            'EQUAL': '=',
        }

        # Handle keyboard
        parts = action_str.split("+")
        readable_parts = []

        for part in parts:
            part = part.strip()
            # Convert KEY_* to readable names
            if part.startswith("KEY_"):
                original_part = part
                key_name = part.replace("KEY_", "")

                # Don't strip LEFT/RIGHT from arrow keys and navigation keys
                if original_part not in ('KEY_LEFT', 'KEY_RIGHT', 'KEY_UP', 'KEY_DOWN'):
                    # Clean up modifier names
                    key_name = key_name.replace("LEFT", "").replace("RIGHT", "")

                # Special cases
                if key_name == "META":
                    key_name = "Super"
                # Check if it's a symbol key
                elif key_name in SYMBOL_MAP:
                    key_name = SYMBOL_MAP[key_name]
                else:
                    # Replace underscores with spaces for readability
                    key_name = key_name.replace('_', ' ')
                    # Title case for regular keys
                    key_name = key_name.title()
                readable_parts.append(key_name)
            else:
                readable_parts.append(part)

        return "+".join(readable_parts)

    def keyPressEvent(self, event):
        """Handle keyboard navigation between panes with left/right arrows"""
        from PySide6.QtWidgets import QLineEdit, QComboBox, QTextEdit

        # Don't intercept if user is typing in a text field or interacting with a dropdown
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, (QLineEdit, QTextEdit)):
            # Let the text field handle the key press
            super().keyPressEvent(event)
            return

        # Don't intercept if a combo box is open
        if isinstance(focused_widget, QComboBox):
            super().keyPressEvent(event)
            return

        key = event.key()

        # Define the navigation order for the three main panes
        focusable_widgets = [
            self.profile_manager.profile_table,  # Access the QTableWidget inside ProfileManager
            self.controls_list.table,            # Access the QTableWidget inside ControlsList
            self.control_editor                  # The ControlEditor widget itself
        ]

        # Find current focus position
        current_index = -1
        for i, widget in enumerate(focusable_widgets):
            if widget.hasFocus() or widget.isAncestorOf(focused_widget) if focused_widget else False:
                current_index = i
                break

        # Handle left/right arrow keys
        if key == Qt.Key_Right:
            # Move to next pane (with wrap-around)
            next_index = (current_index + 1) % len(focusable_widgets)
            focusable_widgets[next_index].setFocus()
            logger.debug(f"Focus moved right to pane {next_index}")
        elif key == Qt.Key_Left:
            # Move to previous pane (with wrap-around)
            prev_index = (current_index - 1) % len(focusable_widgets)
            focusable_widgets[prev_index].setFocus()
            logger.debug(f"Focus moved left to pane {prev_index}")
        else:
            # Pass other keys to parent handler
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close event - restart driver if it was running"""
        logger.info("Main window closing")

        # If in testing mode, stop the driver first
        if self.is_testing:
            logger.info("Closing while in test mode - stopping driver first")
            self._stop_testing()

        # Check for unsaved changes
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Profile '{self.current_profile.name}' has unsaved changes.\n\n"
                "Do you want to save them before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )

            if reply == QMessageBox.Save:
                # Save the changes (both profile metadata and control mappings)
                from .config_writer import profile_exists_in_config
                original_name = self.profile_original_names.get(id(self.current_profile), self.current_profile.name)
                profile_exists = profile_exists_in_config(original_name)

                if not profile_exists:
                    # This is a new profile - create it
                    logger.info(f"Creating new profile on close: {self.current_profile.name}")
                    success = create_new_profile(self.current_profile)
                else:
                    # Existing profile - save metadata and mappings
                    old_name = original_name if original_name != self.current_profile.name else None

                    # Save profile metadata (name, window matching)
                    metadata_success = save_profile_metadata(self.current_profile, old_name)

                    # Save control mappings
                    mappings_success = True
                    if self.modified_mappings:
                        mappings_success = save_profile(self.current_profile, self.modified_mappings)

                    success = metadata_success and mappings_success

                if not success:
                    reply2 = QMessageBox.critical(
                        self,
                        "Save Failed",
                        "Failed to save changes.\n\nClose anyway?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply2 == QMessageBox.No:
                        event.ignore()
                        return
                else:
                    cleanup_old_backups()
            elif reply == QMessageBox.Cancel:
                # Cancel the close
                event.ignore()
                return
            elif reply == QMessageBox.Discard:
                # Just log that we're discarding - changes will be lost on close
                logger.info(f"Discarding changes to {self.current_profile.name} on close")

        # Restart driver if it was running when we started
        if self.driver_was_running:
            logger.info("Restarting driver...")
            self.statusBar().showMessage("Restarting driver...")

            success, message = DriverManager.start_driver()

            if success:
                logger.info("Driver restarted successfully")
            else:
                logger.error(f"Failed to restart driver: {message}")
                reply = QMessageBox.critical(
                    self,
                    "Driver Restart Failed",
                    f"Failed to restart the TourBox driver:\n{message}\n\n"
                    "You may need to restart it manually:\n"
                    "  systemctl --user start tourbox\n\n"
                    "Close anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.No:
                    event.ignore()
                    return
        else:
            logger.info("Driver was not running, not restarting")

        event.accept()


def main():
    """Main entry point for GUI application"""
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("Starting TourBox Elite Configuration GUI")

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("TourBox Elite Configuration")
    app.setDesktopFileName("tourbox-gui.desktop")

    # Create and show main window
    window = TourBoxConfigWindow()
    window.show()

    # Run application event loop
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
