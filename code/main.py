import sys
import time
import csv
import json
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QListWidget, QAbstractItemView, QMessageBox, QDialog, QComboBox,
    QFileDialog, QFormLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

SETTINGS_FILE = "settings.json"
WEEKDAYS = ["maandag", "dinsdag", "woensdag", "donderdag",
            "vrijdag", "zaterdag", "zondag"]

# --------------------- Task ---------------------
class Task:
    def __init__(self, name):
        self.name = name
        self.total_seconds = 0
        self.running = False
        self.start_time = None

    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True

    def pause(self):
        if self.running:
            self.total_seconds += int(time.time() - self.start_time)
            self.start_time = None
            self.running = False

    def get_elapsed(self):
        elapsed = self.total_seconds
        if self.running:
            elapsed += int(time.time() - self.start_time)
        return elapsed

    def get_time_str(self):
        elapsed = self.get_elapsed()
        h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

# --------------------- Settings Dialog ---------------------
class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_folder="", current_theme="System"):
        super().__init__(parent)
        self.setWindowTitle("Instellingen")
        self.setModal(True)
        self.resize(400, 150)

        self.export_folder = current_folder
        self.theme = current_theme

        layout = QFormLayout(self)

        self.folder_input = QLineEdit(self.export_folder)
        self.browse_btn = QPushButton("Bladeren...")
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.browse_btn)
        layout.addRow("CSV Export Folder:", folder_layout)
        self.browse_btn.clicked.connect(self.browse_folder)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        self.theme_combo.setCurrentText(self.theme)
        layout.addRow("Theme:", self.theme_combo)

        self.save_btn = QPushButton("Opslaan")
        layout.addRow(self.save_btn)
        self.save_btn.clicked.connect(self.accept)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Kies map")
        if folder:
            self.folder_input.setText(folder)

    def get_settings(self):
        return {"export_folder": self.folder_input.text(),
                "theme": self.theme_combo.currentText()}

# --------------------- Task Manager ---------------------
class TaskManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Grindstone - Stable macOS")
        self.resize(500, 400)

        self.tasks = []
        self.current_task = None
        self.settings = {"export_folder": "", "theme": "System"}
        self.load_settings()

        self.layout = QVBoxLayout(self)

        # ----------------- Compact timer panel -----------------
        self.compact_panel = QWidget()
        panel_layout = QVBoxLayout(self.compact_panel)
        self.active_task_label = QLabel("No task running")
        self.active_task_label.setAlignment(Qt.AlignCenter)
        self.active_task_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 24px;")
        panel_layout.addWidget(self.active_task_label)
        panel_layout.addWidget(self.timer_label)
        self.layout.addWidget(self.compact_panel)

        # ----------------- Task input -----------------
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Nieuwe taak...")
        self.add_btn = QPushButton("Toevoegen")
        self.remove_btn = QPushButton("Verwijderen")
        self.settings_btn = QPushButton("Instellingen")
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.add_btn)
        input_layout.addWidget(self.remove_btn)
        input_layout.addWidget(self.settings_btn)
        self.layout.addLayout(input_layout)

        # ----------------- Task list -----------------
        self.task_list = QListWidget()
        self.task_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.layout.addWidget(self.task_list)

        # ----------------- Control buttons -----------------
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start / Hervat")
        self.pause_btn = QPushButton("Pauzeer")
        self.export_btn = QPushButton("Exporteer CSV")
        self.mini_mode_btn = QPushButton("Mini Mode")
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.mini_mode_btn)
        self.layout.addLayout(btn_layout)

        # ----------------- Connections -----------------
        self.add_btn.clicked.connect(self.add_task)
        self.task_input.returnPressed.connect(self.add_task)
        self.remove_btn.clicked.connect(self.remove_task)
        self.settings_btn.clicked.connect(self.open_settings)
        self.start_btn.clicked.connect(self.start_task)
        self.pause_btn.clicked.connect(self.pause_task)
        self.export_btn.clicked.connect(self.export_csv)
        self.task_list.itemSelectionChanged.connect(self.update_task_highlight)
        self.mini_mode_btn.clicked.connect(self.toggle_mini_mode)

        self.is_mini_mode = False  # mini mode state

        # ----------------- Timer -----------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)

        self.apply_theme(self.settings.get("theme", "System"))

    # ----------------- Task operations -----------------
    def add_task(self):
        name = self.task_input.text().strip()
        if name:
            task = Task(name)
            self.tasks.append(task)
            self.task_list.addItem(task.name)
            self.task_input.clear()

    def remove_task(self):
        selected_item = self.task_list.currentItem()
        if not selected_item:
            return
        reply = QMessageBox.question(
            self, "Bevestigen",
            f"Weet je zeker dat je '{selected_item.text()}' wilt verwijderen?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.tasks = [t for t in self.tasks if t.name != selected_item.text()]
            self.task_list.takeItem(self.task_list.row(selected_item))
            if self.current_task and self.current_task.name == selected_item.text():
                self.current_task = None
            self.update_task_highlight()

    def start_task(self):
        selected_item = self.task_list.currentItem()
        if not selected_item:
            return
        task_name = selected_item.text()
        for task in self.tasks:
            if task.name != task_name:
                task.pause()
        for task in self.tasks:
            if task.name == task_name:
                task.start()
                self.current_task = task
        self.update_task_highlight()

    def pause_task(self):
        if self.current_task:
            self.current_task.pause()
            self.current_task = None
            self.update_task_highlight()

    # ----------------- UI updates -----------------
    def update_task_highlight(self):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if self.current_task and item.text() == self.current_task.name:
                item.setBackground(QColor("#00FF00"))  # active
            elif item.isSelected():
                item.setBackground(QColor("#3399FF"))  # selected
            else:
                item.setBackground(QColor("transparent"))

    def update_ui(self):
        if self.current_task:
            self.timer_label.setText(self.current_task.get_time_str())
            self.active_task_label.setText(f"Running task: {self.current_task.name}")
        else:
            self.timer_label.setText("00:00:00")
            self.active_task_label.setText("No task running")

    # ----------------- CSV export -----------------
    def export_csv(self):
        if not self.tasks:
            return
        today = datetime.now()
        weekday_name = WEEKDAYS[today.weekday()]
        filename = f"{weekday_name}, {today.strftime('%d.%m.%Y')}_tasks_day.csv"
        export_path = self.settings["export_folder"] if self.settings["export_folder"] else "."
        full_path = os.path.join(export_path, filename)
        try:
            with open(full_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Taak", "Tijd (HH:MM:SS)"])
                for task in self.tasks:
                    writer.writerow([task.name, task.get_time_str()])
            QMessageBox.information(self, "Exporteren", f"CSV opgeslagen als {full_path}")
        except Exception as e:
            QMessageBox.warning(self, "Fout", f"Kon CSV niet opslaan:\n{e}")

    # ----------------- Settings -----------------
    def open_settings(self):
        dlg = SettingsDialog(self,
                             current_folder=self.settings.get("export_folder", ""),
                             current_theme=self.settings.get("theme", "System"))
        if dlg.exec() == QDialog.Accepted:
            self.settings.update(dlg.get_settings())
            self.apply_theme(self.settings["theme"])
            self.save_settings()

    def apply_theme(self, theme):
        if theme == "Dark":
            self.setStyleSheet("background-color: #2b2b2b; color: white;")
        elif theme == "Light":
            self.setStyleSheet("background-color: white; color: black;")
        else:
            self.setStyleSheet("")

    # ----------------- Mini Mode -----------------
    def toggle_mini_mode(self):
        if not self.is_mini_mode:
            # Enter mini mode
            self.setFixedSize(250, 60)
            self.task_list.hide()
            self.add_btn.hide()
            self.remove_btn.hide()
            self.settings_btn.hide()
            self.start_btn.hide()
            self.pause_btn.hide()
            self.export_btn.hide()
            # Make mini mode horizontal layout
            self.compact_panel.layout().setDirection(QVBoxLayout.LeftToRight)
            self.timer_label.setStyleSheet("font-size: 16px;")
            self.active_task_label.setStyleSheet("font-size: 12px; font-weight: bold;")
            self.is_mini_mode = True
        else:
            # Exit mini mode
            self.setFixedSize(500, 400)
            self.task_list.show()
            self.add_btn.show()
            self.remove_btn.show()
            self.settings_btn.show()
            self.start_btn.show()
            self.pause_btn.show()
            self.export_btn.show()
            self.compact_panel.layout().setDirection(QVBoxLayout.TopToBottom)
            self.timer_label.setStyleSheet("font-size: 24px;")
            self.active_task_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            self.is_mini_mode = False


    def mouseDoubleClickEvent(self, event):
        if self.is_mini_mode:
            self.toggle_mini_mode()

    # ----------------- Persistent settings -----------------
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    self.settings.update(json.load(f))
            except:
                pass

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f)
        except Exception as e:
            QMessageBox.warning(self, "Fout", f"Kon instellingen niet opslaan:\n{e}")

# --------------------- Run Application ---------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec())
