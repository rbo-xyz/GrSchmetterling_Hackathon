#um den Designer zu laden
# "C:\Users\"user"\anaconda3\envs\"envname"\Library\bin\Designer6.exe"

#import Files für Berechnung
from src.calculate import calc_leistungskm
from src.import_gpx import import_gpx, identify_source
from src.maps import generate_elevation_plot, generate_route_map
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
import os
import platform
import subprocess

# UI aus .py-Datei importieren
# from src.UserInterface_ui_embedded import Ui_MarschzeitBerechnung

## Generierung des .py-Files aus der .ui Datei --> Eingabe im Terminal
#  pyuic5 -x src/UserInterface.ui -o src/UserInterface_ui_embedded.py

class MarschzeitFenster(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("src/UserInterface.ui", self)  # UI laden

        # self.ui = Ui_MarschzeitBerechnung()
        # self.ui.setupUi(self)

        self.setWindowIcon(QIcon("icons/logo.png"))
        self.setWindowTitle("Marschzeitberechnung")
        self.setMinimumSize(1000, 800)
        self.resize(1800, 1200)
        self.ui.dateEditDatum.setDate(QDate.currentDate())

        #Matplotlib Figur initialisieren
        self.fig = None

        if self.ui.groupBoxHoehenprofil.layout() is None:
            self.ui.groupBoxHoehenprofil.setLayout(QVBoxLayout())
        self.ui.groupBoxHoehenprofil.setMinimumHeight(500)



        # Button Verbindungen
        
        self.ui.pushButtonLoad.clicked.connect(self.laden)
        self.ui.pushButtonCalculate.clicked.connect(self.calculate)
        self.ui.pushButtonExportPDF.clicked.connect(self.export_pdf)

        
        
        



    #Funktionen für die Berechnung

    def laden(self):
        #Laden der GPX Datei über einen FileDialog
        self.filename_i, type = QFileDialog.getOpenFileName(self, "Datei öffnen",
                                                     "", 
                                                     "GPX-File (*.gpx)")
        #Abfüllen des Dateinamens in der UI
        self.ui.lineEditRoute.setText(self.filename_i)
        return self.filename_i


    def calculate(self):
        #progressbar Value auf 10 setzen
        self.ui.progressBar.setValue(10)

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
                self.ui.progressBar.setValue(0)
                return

            ## Prüfung ob File von Siwsstopo um programmabsturz zu vermeiden
            if identify_source(self.filename_i) == "unknown":
                QMessageBox.critical(self, "Ungültige Eingabe", "Das File ist nicht mit den Tools der swisstopo erstellt worden.")
                self.ui.progressBar.setValue(0)
                return

            self.gdf_imp = import_gpx(self.filename_i)

            #progressbar Value auf 50% setzen
            self.ui.progressBar.setValue(50)


            # Zugriff auf die Meta-Informationen aus dem UI (hier eingesetzt, da die Variablen abgefüllt sein müssen!)
            self.input_titel = self.ui.lineEditTitel.text().strip()
            #Abrage ob Geschwindikeit eingegeben wurde um Programmabsturz zu vermeiden
            try:
                self.input_geschwindigkeit = float(self.ui.lineEditSpeed.text().strip())
            except ValueError:
                QMessageBox.critical(self, "Ungültige Eingabe", "Bitte eine gültige Geschwindigkeit in km/h eingeben.")
                self.ui.progressBar.setValue(0)
                return
            self.input_ersteller = self.ui.lineEditErsteller.text().strip()
            self.input_erstellerdatum = self.ui.dateEditDatum.date().toString("dd.MM.yyyy")


            # Berechnung der Leistungskilometer, Marschzeit, Distanz und Höhenmeter
            self.gdf_calc, self.tot_dist, self.tot_lkm, self.tot_hm_pos, self.tot_hm_neg, self.tot_marschzeit_h, self.tot_marschzeit_min = calc_leistungskm(self.gdf_imp, self.input_geschwindigkeit)
            
            


            #progressbar Value auf 75% setzen
            self.ui.progressBar.setValue(75)
            

            #Darstellung des Dataframes (als Tabelle) im UI
            self.gdf_show = show(self.gdf_calc)
            self.ui.tableWidget.setRowCount(len(self.gdf_show))
            self.ui.tableWidget.setColumnCount(len(self.gdf_show.columns))
            self.ui.tableWidget.setHorizontalHeaderLabels(self.gdf_show.columns.tolist())

            for row_idx in range(len(self.gdf_show)):
                for col_idx, col_name in enumerate(self.gdf_show.columns):
                    item = QTableWidgetItem(str(self.gdf_show.iloc[row_idx, col_idx]))
                    self.ui.tableWidget.setItem(row_idx, col_idx, item)
            

            #progressbar Value auf 85% setzen
            self.ui.progressBar.setValue(85)

            #Darstellung des Höhenprofils (interaktiv) im UI
            self.fig = generate_elevation_plot(self.gdf_calc)
        

            layout = self.ui.groupBoxHoehenprofil.layout()
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

            #generierung der Karte
            generate_route_map(self.gdf_calc)
            


            #progressbar Value auf 95% setzen
            self.ui.progressBar.setValue(95)
            

            # Abfüllen der Summary im UI
            self.ui.labelSummary.setText(f"Gesamtsumme: Distanz: {self.tot_dist} km bzw. {self.tot_lkm} lkm | Hoehenmeter: {self.tot_hm_pos} m und {self.tot_hm_neg} m | Marschzeit: {self.tot_marschzeit_h}:{self.tot_marschzeit_min} h")
            # Ausgabe des Geodatframes für den Export

            #progressbar Value auf 100% setzen
            self.ui.progressBar.setValue(100)

            return self.gdf_calc

        


    def export_pdf(self):
        #progressbar Value auf 10 setzen
        self.ui.progressBar.setValue(10)

        
        self.filename_s, typ= QFileDialog.getSaveFileName(self, "Datei Speichern",
                                                   "",
                                                   "PDF (*.PDF)")
        #progressbar Value auf 30 setzen
        self.ui.progressBar.setValue(30)

        # Abfrage des Exportformats aus dem Droppdown Menü
        self.export_format = self.comboBoxExportFormat.currentText()

        export_to_pdf(self.gdf_calc, self.filename_s,self.input_geschwindigkeit, self.tot_dist, self.tot_lkm, self.tot_hm_pos, self.tot_hm_neg, self.tot_marschzeit_h, self.tot_marschzeit_min, self.input_titel, self.input_ersteller, self.input_erstellerdatum, self.export_format)
        
        #progressbar Value auf 90 setzen
        self.ui.progressBar.setValue(90)

        # PDF automatisch öffnen
        if self.filename_s:
            if platform.system() == 'Windows':
                os.startfile(self.filename_s)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', self.filename_s])
            else:  # Linux
                subprocess.call(['xdg-open', self.filename_s])

        #progressbar Value auf 100 setzen
        self.ui.progressBar.setValue(100)

        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenster = MarschzeitFenster()
    fenster.show()
    sys.exit(app.exec_())
