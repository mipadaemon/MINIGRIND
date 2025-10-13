import sys
import time
import csv
import json
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QListWidget, QAbstractItemView, QMessageBox, QDialog, QComboBox,
    QFileDialog, QFormLayout, QCheckBox
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
    
    def get_task_date(self):
        task_date = datetime.fromtimestamp(self.start_time) if self.start_time else datetime.now()
        return task_date.strftime("%a, %d.%m.%Y")

# --------------------- Settings Dialog ---------------------
class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_folder="", current_theme="System", predefined_tasks=None, auto_load_predefined=True):
        super().__init__(parent)
        self.setWindowTitle("Instellingen")
        self.setModal(True)
        self.resize(400, 350)

        self.export_folder = current_folder
        self.theme = current_theme
        self.predefined_tasks = predefined_tasks or []
        self.auto_load_predefined = auto_load_predefined

        layout = QVBoxLayout(self)

        # ---- Export folder ----
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit(self.export_folder)
        self.browse_btn = QPushButton("Bladeren...")
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.browse_btn)
        layout.addLayout(folder_layout)
        self.browse_btn.clicked.connect(self.browse_folder)

        # Disable auto default behavior
        for btn in [self.browse_btn]:
            btn.setAutoDefault(False)
            btn.setDefault(False)

        # ---- Theme ----
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        self.theme_combo.setCurrentText(self.theme)
        layout.addWidget(QLabel("Thema:"))
        layout.addWidget(self.theme_combo)

        # ---- Predefined tasks ----
        layout.addWidget(QLabel("Voorgedefinieerde taken:"))
        self.task_list = QListWidget()
        self.task_list.addItems(self.predefined_tasks)
        layout.addWidget(self.task_list)

        btn_task_layout = QHBoxLayout()
        self.new_task_input = QLineEdit()
        self.new_task_input.setPlaceholderText("Nieuwe taaknaam...")
        self.add_task_btn = QPushButton("Toevoegen")
        self.remove_task_btn = QPushButton("Verwijderen")
        btn_task_layout.addWidget(self.new_task_input)
        btn_task_layout.addWidget(self.add_task_btn)
        btn_task_layout.addWidget(self.remove_task_btn)
        layout.addLayout(btn_task_layout)

        self.add_task_btn.clicked.connect(self.add_task)
        self.remove_task_btn.clicked.connect(self.remove_task)
        self.new_task_input.returnPressed.connect(self.add_task)

        for btn in [self.add_task_btn, self.remove_task_btn]:
            btn.setAutoDefault(False)
            btn.setDefault(False)

        # ---- Checkbox for auto load ----
        self.auto_load_checkbox = QCheckBox("Laad voorgedefinieerde taken automatisch bij opstarten")
        self.auto_load_checkbox.setChecked(self.auto_load_predefined)
        layout.addWidget(self.auto_load_checkbox)

        # ---- Save ----
        self.save_btn = QPushButton("Opslaan")
        layout.addWidget(self.save_btn)
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setAutoDefault(False)
        self.save_btn.setDefault(False)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Kies map")
        if folder:
            self.folder_input.setText(folder)

    def add_task(self):
        name = self.new_task_input.text().strip()
        if name and name not in [self.task_list.item(i).text() for i in range(self.task_list.count())]:
            self.task_list.addItem(name)
            self.new_task_input.clear()

    def remove_task(self):
        selected = self.task_list.currentItem()
        if selected:
            self.task_list.takeItem(self.task_list.row(selected))

    def get_settings(self):
        tasks = [self.task_list.item(i).text() for i in range(self.task_list.count())]
        return {
            "export_folder": self.folder_input.text(),
            "theme": self.theme_combo.currentText(),
            "predefined_tasks": tasks,
            "auto_load_predefined": self.auto_load_checkbox.isChecked()
        }

# --------------------- Task Manager ---------------------
class TaskManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MiniGrind - by MipADeV")
        self.resize(500, 400)

        self.tasks = []
        self.current_task = None
        self.settings = {"export_folder": "", "theme": "System", "predefined_tasks": [], "auto_load_predefined": True}
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

        # ⚙️ Settings button (Unicode gear)
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setToolTip("Instellingen")
        self.settings_btn.setFixedWidth(35)

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

        self.is_mini_mode = False

        # ----------------- Timer -----------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)

        self.apply_theme(self.settings.get("theme", "System"))

        # Load predefined tasks (if enabled)
        if self.settings.get("auto_load_predefined", True):
            self.load_predefined_tasks()

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
                item.setBackground(QColor("#00FF00"))
            elif item.isSelected():
                item.setBackground(QColor("#3399FF"))
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
            QMessageBox.information(self, "Geen taken", "Er zijn geen taken om te exporteren.")
            return

        today = datetime.now()
        weekday_name = WEEKDAYS[today.weekday()]
        timestamp = today.strftime("%H-%M-%S")
        filename = f"{weekday_name}, {today.strftime('%d.%m.%Y')}_{timestamp}_tasks_day.csv"
        export_path = self.settings["export_folder"] if self.settings["export_folder"] else "."
        full_path = os.path.join(export_path, filename)

        try:
            with open(full_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Datum", "Taak", "Tijd (HH:MM:SS)"])
                for task in self.tasks:
                    writer.writerow([task.get_task_date(), task.name, task.get_time_str()])
            QMessageBox.information(self, "Exporteren", f"CSV opgeslagen als:\n{full_path}")
        except Exception as e:
            QMessageBox.warning(self, "Fout", f"Kon CSV niet opslaan:\n{e}")

    # ----------------- Settings -----------------
    def open_settings(self):
        dlg = SettingsDialog(
            self,
            current_folder=self.settings.get("export_folder", ""),
            current_theme=self.settings.get("theme", "System"),
            predefined_tasks=self.settings.get("predefined_tasks", []),
            auto_load_predefined=self.settings.get("auto_load_predefined", True)
        )
        if dlg.exec() == QDialog.Accepted:
            self.settings.update(dlg.get_settings())
            self.apply_theme(self.settings["theme"])
            self.save_settings()
            if self.settings.get("auto_load_predefined", True):
                self.load_predefined_tasks()

    def load_predefined_tasks(self):
        predefined = self.settings.get("predefined_tasks", [])
        if predefined:
            self.task_list.clear()
            self.tasks = []
            for name in predefined:
                task = Task(name)
                self.tasks.append(task)
                self.task_list.addItem(task.name)

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
            self.setFixedSize(300, 80)
            self.task_input.hide()
            self.task_list.hide()
            self.add_btn.hide()
            self.remove_btn.hide()
            self.settings_btn.hide()
            self.start_btn.hide()
            self.pause_btn.hide()
            self.export_btn.hide()
            self.mini_mode_btn.hide()

            old_layout = self.compact_panel.layout()
            if old_layout:
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                QWidget().setLayout(old_layout)

            new_layout = QHBoxLayout(self.compact_panel)
            new_layout.addWidget(self.active_task_label)
            new_layout.addWidget(self.timer_label)

            self.timer_label.setStyleSheet("font-size: 16px; margin-left: 10px;")
            self.active_task_label.setStyleSheet("font-size: 12px; font-weight: bold;")
            self.is_mini_mode = True
        else:
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.resize(500, 400)

            self.task_input.show()
            self.task_list.show()
            self.add_btn.show()
            self.remove_btn.show()
            self.settings_btn.show()
            self.start_btn.show()
            self.pause_btn.show()
            self.export_btn.show()
            self.mini_mode_btn.show()

            old_layout = self.compact_panel.layout()
            if old_layout:
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                QWidget().setLayout(old_layout)

            new_layout = QVBoxLayout(self.compact_panel)
            new_layout.addWidget(self.active_task_label)
            new_layout.addWidget(self.timer_label)

            self.timer_label.setStyleSheet("font-size: 24px;")
            self.active_task_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            self.active_task_label.setAlignment(Qt.AlignCenter)
            self.timer_label.setAlignment(Qt.AlignCenter)
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
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Fout", f"Kon instellingen niet opslaan:\n{e}")

# --------------------- Run Application ---------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec())