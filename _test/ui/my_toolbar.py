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

'''
    A custom toolbar with a dropdown and two buttons.
    The dropdown selects a review level.
    The thumb down button rejects the current image with the selected review level.
    The thumb up button accepts the current image with the selected review level.
'''
basedir = os.path.dirname(__file__)

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