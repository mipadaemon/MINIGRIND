from PySide6.QtWidgets import QApplication, QLabel
import sys

app = QApplication(sys.argv)
label = QLabel("Hello world")
label.show()
sys.exit(app.exec())
