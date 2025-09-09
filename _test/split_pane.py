import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QTabWidget,
    QLabel,
)
from widgets.qtreeview_media_scanner import MediaScannerWidget

'''
    Generate a pyqt6 program with a two panes and a vertical split.
    The left pane should have 1/3 of the window and the right should have 2/3. 
    When the window is resized only the right pane should change size. 
    The right pane should contain two tabs.
'''
class LeftPane(QWidget):
    """A placeholder widget for the non-resizable left pane."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Left Pane (fixed size)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setStyleSheet("background-color: #f0f0f0;")

class RightPane(QWidget):
    """A container for the tab widget in the resizable right pane."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(QLabel("This is Tab 1"), "Tab 1")
        self.tab_widget.addTab(QLabel("This is Tab 2"), "Tab 2")
        layout.addWidget(self.tab_widget)
        self.setStyleSheet("background-color: #e0e0e0;")

class MainWindow(QMainWindow):
    """The main window of the application."""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Two-Pane Window with Fixed Left Pane")
        self.setGeometry(100, 100, 900, 600)

        # Create the splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create the left and right panes
        self.left_pane = MediaScannerWidget()
        self.right_pane = RightPane()

        # Add the panes to the splitter
        splitter.addWidget(self.left_pane)
        splitter.addWidget(self.right_pane)
        
        # Set the initial sizes to achieve the 1/3 and 2/3 ratio.
        # The numbers are pixels, but the stretch factors below will
        # ensure the desired resizing behavior.
        initial_width = self.width()
        left_width = int(initial_width / 3)
        right_width = int(initial_width * 2 / 3)
        splitter.setSizes([left_width, right_width])

        # Make the left pane fixed and the right pane resizable
        # A stretch factor of 0 prevents resizing, and 1 allows it.
        splitter.setStretchFactor(0, 0) # Left pane (fixed)
        splitter.setStretchFactor(1, 1) # Right pane (resizable)

        # Set the splitter as the central widget of the main window
        self.setCentralWidget(splitter)

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
