#um den Designer zu laden
# "C:\Users\"user"\anaconda3\envs\"envname"\Library\bin\Designer6.exe"

#import Files für Berechnung
from src.calculate import calc_leistungskm
from src.import_gpx import import_gpx, identify_source
from src.maps import generate_elevation_plot 
from src.export import export_to_pdf
from src.gdf_show import show

#import Module
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox,QGraphicsScene,QTableWidget, QTableWidgetItem, QBoxLayout, QVBoxLayout
from PyQt5.QtCore import QUrl, QDate
from PyQt5.QtGui import QPixmap, QIcon
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pandas as pd
import xml.etree.ElementTree as ET



class MarschzeitBerechnung(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/UserInterface.ui", self)  # UI laden

        self.setWindowIcon(QIcon("icons/logo.png"))
        self.setWindowTitle("Marschzeitberechnung")
        self.setMinimumSize(1000, 800)
        self.resize(1800, 1200)
        self.dateEditDatum.setDate(QDate.currentDate())

        #Matplotlib Figur initialisieren
        self.fig = None

        if self.groupBoxHoehenprofil.layout() is None:
            self.groupBoxHoehenprofil.setLayout(QVBoxLayout())
        self.groupBoxHoehenprofil.setMinimumHeight(500)



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
        #progressbar Value auf 10 setzen
        self.progressBar.setValue(10)

        #Kontrolle ob eine Datei geladen wurde
        if not hasattr(self, 'filename_i') or not self.filename_i:
            QMessageBox.critical(self, "Fehler", "Bitte laden Sie zuerst eine GPX-Datei.")
            return  # Berechnung abbrechen
        else:
            #import der GPX Datei über den Importer

            ## Prüfung ob das File dem Stansard entspricht um programmabsturz zu vermeiden
            try:
                ET.parse(self.filename_i)
            except ET.ParseError as e:
                QMessageBox.critical(self, "Ungültige Eingabe", "Das File ist nicht lesbar.")
                self.progressBar.setValue(0)
                return

            ## Prüfung ob File von Siwsstopo um programmabsturz zu vermeiden
            if identify_source(self.filename_i) == "unknown":
                QMessageBox.critical(self, "Ungültige Eingabe", "Das File ist nicht mit den Tools der swisstopo erstellt worden.")
                self.progressBar.setValue(0)
                return

            self.gdf_imp = import_gpx(self.filename_i)
            print("Import wurde ausgeführt")

            #progressbar Value auf 50% setzen
            self.progressBar.setValue(50)


            # Zugriff auf die Meta-Informationen aus dem UI (hier eingesetzt, da die Variablen abgefüllt sein müssen!)
            self.input_titel = self.lineEditTitel.text().strip()
            #Abrage ob Geschwindikeit eingegeben wurde um Programmabsturz zu vermeiden
            try:
                self.input_geschwindigkeit = float(self.lineEditSpeed.text().strip())
            except ValueError:
                QMessageBox.critical(self, "Ungültige Eingabe", "Bitte eine gültige Geschwindigkeit in km/h eingeben.")
                self.progressBar.setValue(0)
                return
            self.input_ersteller = self.lineEditErsteller.text().strip()
            self.input_erstellerdatum = self.dateEditDatum.date().toString("dd.MM.yyyy")


            # Berechnung der Leistungskilometer, Marschzeit, Distanz und Höhenmeter
            self.gdf_calc, self.tot_dist, self.tot_lkm, self.tot_hm_pos, self.tot_hm_neg, self.tot_marschzeit_h, self.tot_marschzeit_min = calc_leistungskm(self.gdf_imp, self.input_geschwindigkeit)
            print("Berechnung wurde ausgeführt")
            # self.gdf_calc.to_csv("test_2.csv")


            #progressbar Value auf 75% setzen
            self.progressBar.setValue(75)
            

            #Darstellung des Dataframes (als Tabelle) im UI
            self.gdf_show = show(self.gdf_calc)
            self.tableWidget.setRowCount(len(self.gdf_show))
            self.tableWidget.setColumnCount(len(self.gdf_show.columns))
            self.tableWidget.setHorizontalHeaderLabels(self.gdf_show.columns.tolist())

            for row_idx in range(len(self.gdf_show)):
                for col_idx, col_name in enumerate(self.gdf_show.columns):
                    item = QTableWidgetItem(str(self.gdf_show.iloc[row_idx, col_idx]))
                    self.tableWidget.setItem(row_idx, col_idx, item)
            print("Dataframe wurde dargestellt")

            #progressbar Value auf 85% setzen
            self.progressBar.setValue(85)

            #Darstellung des Höhenprofils (interaktiv) im UI
            self.fig = generate_elevation_plot(self.gdf_calc)
            print(type(self.fig))

            layout = self.groupBoxHoehenprofil.layout()
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            
            self.canvas = FigureCanvas(self.fig)
            layout.addWidget(self.canvas)

            self.toolbar = NavigationToolbar(self.canvas, self)
            layout.addWidget(self.toolbar)
            self.canvas.draw()
            


            #progressbar Value auf 95% setzen
            self.progressBar.setValue(95)
            

            # Abfüllen der Summary im UI
            self.labelSummary.setText(f"Gesamtsumme: Distanz: {self.tot_dist} km bzw. {self.tot_lkm} lkm | Hoehenmeter: {self.tot_hm_pos} m und {self.tot_hm_neg} m | Marschzeit: {self.tot_marschzeit_h}:{self.tot_marschzeit_min} h")
            # Ausgabe des Geodatframes für den Export

            #progressbar Value auf 100% setzen
            self.progressBar.setValue(100)

            return self.gdf_calc

        


    def export_pdf(self):
        #progressbar Value auf 10 setzen
        self.progressBar.setValue(10)

        print("PDF exportieren wurde gedrückt")
        self.filename_s, typ= QFileDialog.getSaveFileName(self, "Datei Speichern",
                                                   "",
                                                   "PDF (*.PDF)")
        #progressbar Value auf 30 setzen
        self.progressBar.setValue(30)
        print(self.filename_s)
        print(self.input_geschwindigkeit)
        print(self.tot_dist)
        print(self.tot_hm_pos)
        print(self.tot_hm_neg)
        print(self.tot_marschzeit_h)
        print(self.tot_marschzeit_min)
        print(self.input_titel)
        print(self.input_ersteller)
        print(self.input_erstellerdatum)

        export_to_pdf(self.gdf_calc, self.filename_s,self.input_geschwindigkeit, self.tot_dist, self.tot_lkm, self.tot_hm_pos, self.tot_hm_neg, self.tot_marschzeit_h, self.tot_marschzeit_min, self.input_titel, self.input_ersteller, self.input_erstellerdatum)
        
        #progressbar Value auf 100 setzen
        self.progressBar.setValue(100)
        print("Export wurde ausgeführt")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenster = MarschzeitBerechnung()
    fenster.show()
    sys.exit(app.exec_())
