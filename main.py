from shoptimiser_controller import Shoptimiser
from PySide6.QtWidgets import QApplication
import sys
import os

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    spt = Shoptimiser()
    spt.window.show()
    sys.exit(app.exec())

