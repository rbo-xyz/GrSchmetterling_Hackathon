# import andere Dateien
# from import_gpx import parse_gpx
# from calculate import calculate_lkm
# from result import generate_report

# import Module
from PyQt5.QtWidgets import*
from PyQt5.uic import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *

class fenster(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('UI/possible_UI.ui', self)

    


app = QApplication ([])

window = fenster()
window.show()

app.exec()
