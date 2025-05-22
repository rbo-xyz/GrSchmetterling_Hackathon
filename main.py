# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget
from import_gpx import parse_gpx
from calculate import calculate_lkm
from result import generate_report

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pfadi Butterfly Route Planner")

        layout = QVBoxLayout()
        self.import_button = QPushButton("Import GPX File")
        self.import_button.clicked.connect(self.load_gpx)

        layout.addWidget(self.import_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_gpx(self):
        gpx_path, _ = QFileDialog.getOpenFileName(self, "Open GPX File", "", "GPX Files (*.gpx)")
        if gpx_path:
            points = parse_gpx(gpx_path)
            lkm, march_time = calculate_lkm(points)
            generate_report(points, lkm, march_time)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
