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

class MainWindow(QMainWindow):
    def __init__(self,click_notify=None):
        super().__init__()

        v = QVBoxLayout()
        h = QHBoxLayout()

        for a in range(10):
            button = QPushButton(str(a))
            button.clicked.connect(self.button_clicked)

            if click_notify:
                button.clicked.connect(click_notify)
            
            h.addWidget(button)

        v.addLayout(h)
        self.label = QLabel("")
        v.addWidget(self.label)

        w = QWidget()
        w.setLayout(v)
        self.setCentralWidget(w)

    def notify_me(self, method):
        print(f"notify_me: {method}")
        self.button.clicked.connect(method)


    def button_clicked(self, n):
        button = QObject.sender(self)
        text = button.text()
        self.label.setText(text)


class test(QObject):
    def handle_click(self, n):
        button = QObject.sender(self)
        text = button.text()
        print(f"test: {text}")

app = QApplication(sys.argv)

t = test()
window = MainWindow(t.handle_click)

window.show()
app.exec()
