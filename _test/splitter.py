import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QTextEdit,
    QWidget,
    QVBoxLayout,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 Vertical Split Window")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        # Create the QSplitter and set its orientation to horizontal
        # This seems backwards but it creates a vertical split
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create two widgets to place inside the splitter
        top_widget = QTextEdit("This is the top widget.")
        bottom_widget = QTextEdit("This is the bottom widget.")
        
        # You can add any widget, not just QTextEdit.
        # For example:
        # top_widget = QWidget()
        # top_layout = QVBoxLayout(top_widget)
        # top_layout.addWidget(QPushButton("Button in Top Pane"))
        
        # Add the widgets to the splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)

        # Set the initial sizes of the two split areas
        # The list of integers represents the initial size for each widget
        splitter.setSizes([300, 300]) 

        # Create a central widget and set a layout for it
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(splitter)
        
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
