import sys
import os
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QWidget,
    QVBoxLayout,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QLabel,
    QComboBox,
)
from ui.qtreeview_media_scanner import MediaScannerWidget
from ui.image_viewer_widget import ImageGrid

from paths import Paths

basedir = os.path.dirname(__file__)

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

review_list = ["Reject?", "Poor Quality?", "Duplicate?", "Just Okay?", "Good, not Great?"]
rejected_text_list = [text[:-1] for text in review_list]
accepted_text_list = [f"Pass {text[:-1]} Check" for text in review_list]
accepted_text_list[-1] = "Great!"

class MyToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.setIconSize(QSize(16, 16))

        self.dropdown = QComboBox()
        self.dropdown.addItems(review_list)
        self.addWidget(self.dropdown)
        self.dropdown.currentIndexChanged.connect(self.on_dropdown_change)

        # Add reject button
        self.button_action_reject = QAction(
            QIcon(Paths.icon("thumb.png")),
            rejected_text_list[0],
            self,
        )
        self.button_action_reject.setStatusTip(rejected_text_list[0])
        self.button_action_reject.triggered.connect(self.rejectImages)
        self.button_action_reject.setCheckable(False)
        self.addAction(self.button_action_reject)

        # Add accept button
        self.button_action_accept = QAction(
            QIcon(Paths.icon("thumb-up.png")),
            accepted_text_list[0],
            self,
        )
        self.button_action_accept.setStatusTip(accepted_text_list[0])
        self.button_action_accept.triggered.connect(self.acceptImages)
        self.button_action_accept.setCheckable(False)
        self.addAction(self.button_action_accept)

    def rejectImages(self, is_checked):
        print(rejected_text_list[self.dropdown.currentIndex()])

    def acceptImages(self, is_checked):
        print(accepted_text_list[self.dropdown.currentIndex()])

    def on_dropdown_change(self, index):
        print(f"Selected: {self.dropdown.itemText(index)}")
        self.button_action_reject.setText(rejected_text_list[index])
        self.button_action_reject.setStatusTip(rejected_text_list[index])
        self.button_action_accept.setText(accepted_text_list[index])
        self.button_action_accept.setStatusTip(accepted_text_list[index])

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
        self.image_grid = ImageGrid()
        self.right_pane = RightPane()
        self.right_pane.tab_widget.clear()
        self.right_pane.tab_widget.addTab(self.image_grid, "Images")
        self.right_pane.tab_widget.addTab(QLabel("This is Tab 2"), "Tab 2")

        # Add the panes to the splitter
        splitter.addWidget(self.left_pane)
        splitter.addWidget(self.right_pane)
        
        # Add toolbar
        self.addToolBar(MyToolBar(self))
        self.setStatusBar(QStatusBar(self))

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
