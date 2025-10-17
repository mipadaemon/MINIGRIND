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
  <p align="center">
  <img width="760" height="540" alt="image" src="https://github.com/user-attachments/assets/a7d53995-da1a-43b4-92a3-dd12e4fceda3" />
  </p>
  
- Settings Dialog with predefined tasks
  <p align="center">
  <img width="512" height="490" alt="image" src="https://github.com/user-attachments/assets/f0de92d3-af80-49e5-8cee-ce8a31688d2c" />
  </p>
  
- Quick Tasks
  <p align="center">
  <img width="412" height="290" alt="image" src="https://github.com/user-attachments/assets/5d8c8127-a04f-4a17-93e9-a4798eb78885" />
  </p>

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
## 🧾 License

This project is licensed under the [GNU GPL v3 License](LICENSE).  
You’re free to use, modify, and distribute this code — but derivatives must remain open source and credit the original author.

Contact

Developed by MipadaemoN - MipADeV

Feel free to open issues, fork, or contribute!
