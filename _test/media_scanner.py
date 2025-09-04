import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QTreeView, QFileDialog, QHeaderView
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class MediaScannerApp(QMainWindow):
    """
    A PyQt6 application to scan a folder for media files (images and videos)
    and display their names and sizes in a QTreeView.
    """
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.setWindowTitle("Media File Scanner")
        self.setGeometry(100, 100, 700, 500) # x, y, width, height

        # --- Define Media Extensions ---
        self.IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
        self.VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv')
        self.MEDIA_EXTENSIONS = self.IMAGE_EXTENSIONS + self.VIDEO_EXTENSIONS

        # --- Central Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # --- QTreeView for displaying results ---
        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['File Name', 'Size (KB)'])
        self.tree_view.setModel(self.model)
        
        # --- UI Polish: Adjust column widths ---
        # Make the first column (File Name) stretch to fill available space
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        # Resize the second column (Size) to fit its contents
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        # --- "Open Folder" Button ---
        self.open_button = QPushButton("Open Folder")
        self.open_button.clicked.connect(self.open_folder_dialog)

        # --- Add widgets to the layout ---
        layout.addWidget(self.tree_view)
        layout.addWidget(self.open_button)

    def open_folder_dialog(self):
        """
        Opens a dialog to select a folder and initiates the scan if a folder is chosen.
        """
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        
        # Proceed only if the user selected a folder (didn't cancel)
        if folder_path:
            self.scan_folder(folder_path)

    def scan_folder(self, folder_path):
        """
        Recursively scans the given folder for media files and populates the QTreeView.
        """
        # Clear previous results from the model, but keep the headers
        self.model.removeRows(0, self.model.rowCount())
        
        # Use os.walk for efficient recursive traversal
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                # Check if the file has a recognized media extension (case-insensitive)
                if filename.lower().endswith(self.MEDIA_EXTENSIONS):
                    full_path = os.path.join(root, filename)
                    
                    try:
                        # Get file size in bytes and convert to kilobytes
                        size_bytes = os.path.getsize(full_path)
                        size_kb = size_bytes / 1024
                        
                        # Create QStandardItem for the file name and size
                        item_name = QStandardItem(filename)
                        item_size = QStandardItem(f"{size_kb:.2f}") # Format to 2 decimal places
                        
                        # Make items non-editable by the user
                        item_name.setEditable(False)
                        item_size.setEditable(False)
                        
                        # Add the new row to the model
                        self.model.appendRow([item_name, item_size])

                    except OSError as e:
                        # Handle cases where file size can't be read (e.g., permissions)
                        print(f"Error accessing {full_path}: {e}")


# --- Main execution block ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MediaScannerApp()
    window.show()
    sys.exit(app.exec())
    