import sys
import os
import json
import time
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QCheckBox, QFileDialog, QGroupBox,
    QMessageBox
)
from PySide6.QtCore import Qt, QTimer

from src.config.manager import load_config, save_config, get_default_config, get_config_dir
from src.installer.manager import install_hooks, remove_hooks, check_status
from src.audio.player import play_sound, stop_sound

class EventRow(QWidget):
    def __init__(self, title: str, event_key: str, config_data: dict, parent=None):
        super().__init__(parent)
        self.event_key = event_key
        self.config_data = config_data
        self.title = title
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        lbl = QLabel(title)
        lbl.setMinimumWidth(120)
        layout.addWidget(lbl)
        
        # File Path
        self.path_lbl = QLabel(self.config_data.get("sound", ""))
        self.path_lbl.setStyleSheet("color: #666;")
        layout.addWidget(self.path_lbl, stretch=1)
        
        # Browse Button
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse)
        layout.addWidget(browse_btn)
        
        # Preview Button
        self.preview_btn = QPushButton("Preview")
        self.preview_btn.clicked.connect(self.toggle_preview)
        self.is_playing = False
        layout.addWidget(self.preview_btn)
        
        # Enable Toggle
        self.enable_cb = QCheckBox("ON")
        self.enable_cb.setChecked(self.config_data.get("enabled", True))
        self.enable_cb.toggled.connect(self.on_enable_changed)
        layout.addWidget(self.enable_cb)
        
        self.setLayout(layout)
        self.on_enable_changed(self.enable_cb.isChecked())

    def on_enable_changed(self, checked):
        self.enable_cb.setText("ON" if checked else "OFF")
        
    def browse(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Select sound for {self.title}", "", "WAV Files (*.wav)"
        )
        if file_path:
            self.path_lbl.setText(file_path)

    def toggle_preview(self):
        if self.is_playing:
            stop_sound()
            self.preview_btn.setText("Preview")
            self.is_playing = False
        else:
            # We get the volume from the parent window's slider
            volume = self.window().volume_slider.value() / 100.0
            play_sound(self.path_lbl.text(), volume=volume, wait=False)
            self.preview_btn.setText("Stop")
            self.is_playing = True
            
            # Reset button after some time (rough estimate)
            QTimer.singleShot(2000, self.reset_preview_btn)
            
    def reset_preview_btn(self):
        self.preview_btn.setText("Preview")
        self.is_playing = False

    def get_data(self) -> dict:
        return {
            "enabled": self.enable_cb.isChecked(),
            "sound": self.path_lbl.text()
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Antigravity Notify")
        self.setMinimumWidth(600)
        
        self.config = load_config()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(20)
        
        # Master Switch
        self.master_cb = QCheckBox("Enable Notifications")
        self.master_cb.setChecked(self.config.get("enabled", True))
        main_layout.addWidget(self.master_cb)
        
        # Events Group
        events_group = QGroupBox("Events")
        events_layout = QVBoxLayout(events_group)
        
        events_data = self.config.get("events", {})
        self.approval_row = EventRow("Approval Required", "approval", events_data.get("approval", {}), self)
        self.complete_row = EventRow("Task Completed", "complete", events_data.get("complete", {}), self)
        
        events_layout.addWidget(self.approval_row)
        events_layout.addWidget(self.complete_row)
        main_layout.addWidget(events_group)
        
        # Volume Group
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("Notification Volume"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.config.get("volume", 0.8) * 100))
        vol_layout.addWidget(self.volume_slider, stretch=1)
        
        restore_btn = QPushButton("Restore defaults")
        restore_btn.clicked.connect(self.restore_defaults)
        vol_layout.addWidget(restore_btn)
        main_layout.addLayout(vol_layout)
        
        # Status / Install / Save
        bottom_layout = QHBoxLayout()
        
        self.status_lbl = QLabel()
        self.update_status()
        bottom_layout.addWidget(self.status_lbl, stretch=1)
        
        install_btn = QPushButton("Install hooks")
        install_btn.clicked.connect(self.do_install)
        bottom_layout.addWidget(install_btn)
        
        remove_btn = QPushButton("Remove hooks")
        remove_btn.clicked.connect(self.do_remove)
        bottom_layout.addWidget(remove_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_config)
        bottom_layout.addWidget(save_btn)
        
        main_layout.addLayout(bottom_layout)
        
        # Status poller for last event
        self.poller = QTimer(self)
        self.poller.timeout.connect(self.update_status)
        self.poller.start(2000)

    def restore_defaults(self):
        defs = get_default_config()
        self.volume_slider.setValue(int(defs.get("volume", 0.8) * 100))
        self.master_cb.setChecked(defs.get("enabled", True))
        
        for row, key in [(self.approval_row, "approval"), (self.complete_row, "complete")]:
            evt_def = defs.get("events", {}).get(key, {})
            row.enable_cb.setChecked(evt_def.get("enabled", True))
            row.path_lbl.setText(evt_def.get("sound", ""))

    def do_install(self):
        if install_hooks():
            QMessageBox.information(self, "Success", "Hooks installed successfully.")
        else:
            QMessageBox.critical(self, "Error", "Failed to install hooks.")
        self.update_status()

    def do_remove(self):
        if remove_hooks():
            QMessageBox.information(self, "Success", "Hooks removed successfully.")
        else:
            QMessageBox.critical(self, "Error", "Failed to remove hooks.")
        self.update_status()

    def save_config(self):
        self.config["enabled"] = self.master_cb.isChecked()
        self.config["volume"] = self.volume_slider.value() / 100.0
        
        if "events" not in self.config:
            self.config["events"] = {}
            
        self.config["events"]["approval"] = self.approval_row.get_data()
        self.config["events"]["complete"] = self.complete_row.get_data()
        
        try:
            save_config(self.config)
            QMessageBox.information(self, "Saved", "Settings saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{e}")

    def update_status(self):
        installed = check_status()
        status_text = "Hooks: " + ("Installed" if installed else "Not Installed")
        
        # Check last event
        state_path = get_config_dir() / "state.json"
        if state_path.exists():
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                evt = state.get("last_event", "unknown").capitalize()
                ts = state.get("timestamp", 0)
                time_str = time.strftime("%H:%M:%S", time.localtime(ts))
                status_text += f"   Last event: {evt}, {time_str}"
            except Exception:
                pass
                
        self.status_lbl.setText(status_text)
