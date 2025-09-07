import sys

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

''' If a slot is called by a signal, 
    the originating QObject of that signal is available in the slot 
    via QObject.sender()
'''

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        v = QVBoxLayout()
        h = QHBoxLayout()

        for a in range(10):
            button = QPushButton(str(a))
            button.clicked.connect(self.button_clicked)
            h.addWidget(button)

        v.addLayout(h)
        self.label = QLabel("")
        v.addWidget(self.label)

        w = QWidget()
        w.setLayout(v)
        self.setCentralWidget(w)

    def button_clicked(self, n):
        button = QObject.sender(self)
        text = button.text() 
        self.label.setText(text)
        print(text,n)


app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
