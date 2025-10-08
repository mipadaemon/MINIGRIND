# MiniGrind - Task Manager ⏱️

MiniGrind is a lightweight and user-friendly **task and time tracking application** built with **Python** and **PySide6**. It allows you to track multiple tasks, use predefined tasks, export daily logs as CSV, and even work in a compact Mini Mode. Perfect for personal productivity or small project time tracking.

---

## Features

- **Add / Remove tasks** easily in the main interface.
- **Start / Pause** individual tasks.
- **Predefined tasks** in settings for faster startup.
- **Export daily logs to CSV** with automatic timestamp to prevent overwriting.
- **Mini Mode** to keep the app compact on your screen.
- **Dark / Light / System themes**.
- **Persistent settings** saved in `settings.json`.
- **Gear icon button** for quick access to settings.

---

## Screenshots

- Main Task Manager
  <img width="1224" height="1080" alt="image" src="https://github.com/user-attachments/assets/b9fa9142-75ba-4c81-8a95-d747e1f5aaff" />
- Settings Dialog with predefined tasks
  <img width="1024" height="980" alt="image" src="https://github.com/user-attachments/assets/f5ef79f1-d822-435f-a6c3-6c3b8aea27db" />
---
## Start the application
There is a windows executable [MiniGrid_vx.y.z.exe] for download in the releases section --> [Download the latest version](../../releases/latest)

Just download/save it to a directory of your liking, and run it from there.

Another way is to clone the repo and run the main.py (see Installation information below)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/mipadaemon/MiniGrind.git
cd MiniGrind
```
2. Create a virtual environment (optional but recommended):
```
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
```
3. Install dependencies:
```
pip install -r requirements.txt
```
Note: The main dependency is PySide6. You can also install it manually:
```
pip install PySide6
```
Usage
Run the application:
```
python main.py
```
Add a task in the input field and press Enter or Toevoegen.
Select a task and press Start / Hervat to track time.
Pause the active task with Pauzeer.
Export your tasks to CSV using Exporteer CSV (files are timestamped automatically).
Open Settings using the ⚙️ button to add predefined tasks, choose theme, or set the CSV export folder.
Double-click the timer panel or click Mini Mode to switch to compact view.
File Structure
```
MiniGrind/
│
├─ main.py               # Main application
├─ settings.json         # Persistent user settings (auto-generated on first use)
├─ README.md             # This file
└─ requirements.txt      # Python dependencies
```
License
This project is licensed under the MIT License. See LICENSE for details.

Contact
Developed by MipADeV
Feel free to open issues, fork, or contribute!
