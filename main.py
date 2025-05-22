#import Files für Berechnung
from src.calculate import calc_leistungskm
from src.import_gpx import import_gpx

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

        # Button Verbindungen
        
        self.pushButtonLoad.clicked.connect(self.laden)
        self.pushButtonExportPDF.clicked.connect(self.export_pdf)


    #Funktionen für die Berechnung

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
