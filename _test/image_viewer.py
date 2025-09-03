import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class ImageGrid(QMainWindow):
    """
    An image viewer application that displays images in a 3x3 grid.
    Features include opening multiple images and paginating through them.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("3x3 Image Grid Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.image_paths = []
        self.current_page = 0
        self.images_per_page = 9

        # --- UI Setup ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)

        # Grid for images
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5) # small gap between images
        self.main_layout.addLayout(self.grid_layout)

        # Create labels for the grid
        self.image_labels = []
        for i in range(self.images_per_page):
            label = QLabel(f"Image {i+1}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setScaledContents(True) # Key for resizing
            label.setStyleSheet("""
                QLabel {
                    border: 1px solid #CCC;
                    background-color: #F0F0F0;
                    color: #888;
                }
            """)
            self.image_labels.append(label)
            row, col = divmod(i, 3) # Get row and column for 3x3 grid
            self.grid_layout.addWidget(label, row, col)

        # Navigation buttons layout
        self.nav_layout = QHBoxLayout()
        self.main_layout.addLayout(self.nav_layout)
        
        # Create and connect buttons
        self.btn_open = QPushButton("Open Images")
        self.btn_home = QPushButton("<< Home")
        self.btn_prev = QPushButton("< Prev")
        self.btn_next = QPushButton("Next >")
        self.btn_end = QPushButton("End >>")

        self.btn_open.clicked.connect(self.open_images)
        self.btn_home.clicked.connect(self.first_page)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_end.clicked.connect(self.last_page)

        # Add buttons to navigation layout
        self.nav_layout.addWidget(self.btn_open)
        self.nav_layout.addStretch() # Add a spacer
        self.nav_layout.addWidget(self.btn_home)
        self.nav_layout.addWidget(self.btn_prev)
        self.nav_layout.addWidget(self.btn_next)
        self.nav_layout.addWidget(self.btn_end)

        self.update_button_states()

    def open_images(self):
        """Opens a file dialog to select one or more image files."""
        # Supported image file extensions
        file_filter = "Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif)"
        
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select one or more images",
            "", # Start directory
            file_filter
        )

        if paths:
            self.image_paths = paths
            self.current_page = 0
            self.display_page()

    def display_page(self):
        """Updates the grid to show images for the current page."""
        start_index = self.current_page * self.images_per_page
        
        for i in range(self.images_per_page):
            label = self.image_labels[i]
            image_index = start_index + i
            
            if image_index < len(self.image_paths):
                path = self.image_paths[image_index]
                pixmap = QPixmap(path)
                # Scale pixmap to fit the label while keeping aspect ratio
                label.setPixmap(pixmap.scaled(
                    label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            else:
                label.clear() # Clear label if no image
                label.setText(f"Image {i+1}")

        self.update_button_states()

    def update_button_states(self):
        """Enables or disables navigation buttons based on current page."""
        total_images = len(self.image_paths)
        has_images = total_images > 0
        
        # Calculate total pages (0-indexed)
        if not has_images:
            total_pages = 0
        else:
            total_pages = math.ceil(total_images / self.images_per_page) - 1
            
        # Enable/disable buttons
        self.btn_home.setEnabled(has_images and self.current_page > 0)
        self.btn_prev.setEnabled(has_images and self.current_page > 0)
        self.btn_next.setEnabled(has_images and self.current_page < total_pages)
        self.btn_end.setEnabled(has_images and self.current_page < total_pages)
        
    def next_page(self):
        """Goes to the next page of images."""
        total_images = len(self.image_paths)
        total_pages = math.ceil(total_images / self.images_per_page) - 1
        if self.current_page < total_pages:
            self.current_page += 1
            self.display_page()
            
    def prev_page(self):
        """Goes to the previous page of images."""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def first_page(self):
        """Goes to the first page (page 0)."""
        self.current_page = 0
        self.display_page()
        
    def last_page(self):
        """Goes to the final page of images."""
        total_images = len(self.image_paths)
        if total_images > 0:
            self.current_page = math.ceil(total_images / self.images_per_page) - 1
            self.display_page()

    def resizeEvent(self, event):
        """Overrides the resize event to re-scale pixmaps."""
        super().resizeEvent(event)
        # Re-displaying the page on resize will cause pixmaps to be re-scaled
        # based on the new label sizes.
        self.display_page()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageGrid()
    window.show()
    sys.exit(app.exec())
    