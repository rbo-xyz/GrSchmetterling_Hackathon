#import Files für Berechnung
from src.calculate import calc_leistungskm
from src.import_gpx import import_gpx
from src.maps import generate_elevation_plot 
from src.MICHI import export_to_pdf

#import Module
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox,QGraphicsScene,QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd



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
            # self.gdf_calc.to_csv("test.csv")

            #Darstellung des Dataframes im UI
            self.tableWidget.setRowCount(len(self.gdf_calc))
            self.tableWidget.setColumnCount(len(self.gdf_calc.columns))
            self.tableWidget.setHorizontalHeaderLabels(self.gdf_calc.columns.tolist())

            for row_idx in range(len(self.gdf_calc)):
                for col_idx, col_name in enumerate(self.gdf_calc.columns):
                    item = QTableWidgetItem(str(self.gdf_calc.iloc[row_idx, col_idx]))
                    self.tableWidget.setItem(row_idx, col_idx, item)
            print("Dataframe wurde dargestellt")

            #Darstellung des Höhenprofils im UI
            self.fig = generate_elevation_plot(self.gdf_calc)
            self.graphicsViewProfil.setScene(QGraphicsScene())
            canvas = FigureCanvas(self.fig)
            proxy = self.graphicsViewProfil.scene().addWidget(canvas)
            print("Höhenprofil wurde dargestellt")
            

            # Abfüllen der Summary im UI
            self.labelSummary.setText(f"Gesamtsumme: Distanz: {self.tot_dist} km | Hoehenmeter: {self.tot_hm_pos} m und {self.tot_hm_neg} m | Marschzeit: {self.tot_marschzeit_h}:{self.tot_marschzeit_h} h")
            # Ausgabe des Geodatframes für den Export
            return self.gdf_calc

        


    def export_pdf(self):
        print("PDF exportieren wurde gedrückt")
        self.filename_s, typ= QFileDialog.getSaveFileName(self, "Datei Speichern",
                                                   "",
                                                   "PDF (*.PDF)")
        #TODO 
        export_to_pdf(self.gdf_calc, self.filename_s)
        print("Export wurde ausgeführt")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenster = MarschzeitBerechnung()
    fenster.show()
    sys.exit(app.exec_())
