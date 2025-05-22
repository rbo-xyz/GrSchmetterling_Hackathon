#import Files für Berechnung
from src.calculate import calc_leistungskm
from src.import_gpx import import_gpx
from src.maps import generate_elevation_plot 

#import Module
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox,QGraphicsScene
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas



class MarschzeitBerechnung(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("possible_UI.ui", self)  # UI laden

        self.setWindowTitle("Marschzeitberechnung")
        self.setMinimumSize(1000, 800)

        # Button Verbindungen
        
        self.pushButtonLoad.clicked.connect(self.laden)
        self.pushButtonCalculate.clicked.connect(self.calculate)
        self.pushButtonExportPDF.clicked.connect(self.export_pdf)


    #Funktionen für die Berechnung

    def laden(self):
        #Laden der GPX Datei über einen FileDialog
        print("GPX laden wurde gedrückt")
        self.filename_i, type = QFileDialog.getOpenFileName(self, "Datei öffnen",
                                                     "", 
                                                     "GPX-File (*.gpx)")
        #Abfüllen des Dateinamens in der UI
        self.lineEditRoute.setText(self.filename_i)
        return self.filename_i


    def calculate(self):
        print("calculate wurde gedrückt")
        #Kontrolle ob eine Datei geladen wurde
        if not hasattr(self, 'filename_i') or not self.filename_i:
            QMessageBox.critical(self, "Fehler", "Bitte laden Sie zuerst eine GPX-Datei.")
            return  # Berechnung abbrechen
        else:
            #import der GPS Datei über den Importer
            self.gdf_imp = import_gpx(self.filename_i)
            print("Import wurde ausgeführt")
            # Berechnung der Leistungskilometer, Marschzeit, Distanz und Höhenmeter
            self.gdf_calc, self.tot_dist, self.tot_hm_pos, self.tot_hm_neg, self.tot_marschzeit_h, self.tot_marschzeit_min = calc_leistungskm(self.gdf_imp)
            print("Berechnung wurde ausgeführt")
            #Darstellung des Höhenprofils im UI
            #TODO
            self.fig = #TODO
            self.graphicsViewProfil.setScene(QGraphicsScene())
            canvas = FigureCanvas(self.fig)
            proxy = self.graphicsViewProfil.scene().addWidget(canvas)

            # Abfüllen der Summary im UI
            self.labelSummary.setText(f"Gesamtsumme: Distanz: {self.tot_dist} km | Hoehenmeter: {self.tot_hm_pos} m und {self.tot_hm_neg} m | Marschzeit: {self.tot_marschzeit_h}:{self.tot_marschzeit_h} h")
            # Ausgabe des Geodatframes für den Export
            return self.gdf_calc

        # Hier kommt dein Code zum Laden von GPX-Dateien rein


    def hoehenprofil_darstellen(self, bild_pfad):
    # Neue Scene erstellen (oder alte löschen)
        scene = QGraphicsScene()

    # Pixmap aus Bilddatei laden
        pixmap = QPixmap(bild_pfad)

    # Pixmap in die Scene einfügen
        scene.addPixmap(pixmap)

    # Scene in das graphicsView setzen
        self.graphicsViewProfil.setScene(scene)

    # Optional: Ansicht an Pixmapgröße anpassen
        self.graphicsViewProfil.fitInView(scene.itemsBoundingRect(), mode=1)


    def export_pdf(self):
        print("PDF exportieren wurde gedrückt")
        self.filename_s, typ= QFileDialog.getSaveFileName(self, "Datei Speichern",
                                                   "",
                                                   "PDF (*.PDF)")
        #TODO

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenster = MarschzeitBerechnung()
    fenster.show()
    sys.exit(app.exec_())
