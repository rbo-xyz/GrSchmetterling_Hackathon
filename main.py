#import Files für Berechnung
# from src/calculate.py import *

#import Module
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView  # Falls du die Karte einbinden willst
import sys

class MarschzeitBerechnung(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("possible_UI.ui", self)  # UI laden

        self.setWindowTitle("Marschzeitberechnung")
        self.setMinimumSize(1000, 800)

        # Signal-Verbindungen aufbauen
        # Beispiel: Button "GPX laden" heißt in deiner UI 'pushButtonLoad'
        self.pushButtonLoad.clicked.connect(self.laden)
        self.pushButtonExportPDF.clicked.connect(self.export_pdf)

        # Falls du ein QWebEngineView namens 'karte' hast, kannst du z.B. so darauf zugreifen:
        # (Falls nicht vorhanden, muss Widget noch in der UI ergänzt werden)
        # self.karte.load(QUrl('https://www.reddit.com/'))

    def laden(self):
        print("GPX laden wurde gedrückt")

        # Hier kommt dein Code zum Laden von GPX-Dateien rein

    def export_pdf(self):
        print("PDF exportieren wurde gedrückt")
        # Hier kommt dein PDF-Exportcode rein

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenster = MarschzeitBerechnung()
    fenster.show()
    sys.exit(app.exec_())
