# import andere Dateien
# from import_gpx import parse_gpx
# from calculate import calculate_lkm
# from result import generate_report

# import Module
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget
import sys

class MarschzeitBerechnung(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("possible_UI.ui", self)

        # Connect buttons to dummy functions
        self.pushButtonLoad: QPushButton = self.findChild(QPushButton, "pushButtonLoad")
        self.pushButtonLoad.clicked.connect(self.load_gpx_dummy)

        self.pushButtonExportPDF: QPushButton = self.findChild(QPushButton, "pushButtonExportPDF")
        self.pushButtonExportPDF.clicked.connect(self.export_pdf_dummy)

        # Connect table interaction to dummy function
        self.tableWidget: QTableWidget = self.findChild(QTableWidget, "tableWidget")
        self.tableWidget.cellClicked.connect(self.table_cell_clicked_dummy)

    def load_gpx_dummy(self):
        print("🗺️ GPX/KML laden clicked — dummy function")

    def export_pdf_dummy(self):
        print("📝 Export PDF clicked — dummy function")

    def table_cell_clicked_dummy(self, row, column):
        print(f"📋 Table cell clicked at (row={row}, column={column}) — dummy function")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarschzeitBerechnung()
    window.show()
    sys.exit(app.exec_())
