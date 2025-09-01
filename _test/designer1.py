import os
import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication

basedir = os.path.dirname(__file__)

app = QApplication(sys.argv)

window = uic.loadUi(os.path.join(basedir, "ui/first.ui"))
window.show()
app.exec()