# import andere Dateien
# from import_gpx import parse_gpx
# from calculate import calculate_lkm
# from result import generate_report

# import Module
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
import sys

class MarschzeitBerechnung(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("possible_UI.ui", self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarschzeitBerechnung()
    window.show()
    sys.exit(app.exec_())
