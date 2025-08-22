import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
palette = QPalette()
palette.setColor(QPalette.ColorRole.Window, QColor(0, 128, 255))
palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
app.setPalette(palette)

window = QLabel("Palette Test")
window.show()

app.exec()
