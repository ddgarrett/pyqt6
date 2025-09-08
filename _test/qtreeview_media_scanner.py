import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTreeView, QFileDialog, QHeaderView, QSizePolicy
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

MyCustomDataRole = Qt.ItemDataRole.UserRole + 1

class MediaScannerApp(QWidget):
    """
    A PyQt6 application to scan a folder for media files (images and videos)
    and display them in a hierarchical QTreeView that mirrors the folder structure.

    Selecting one or more media files will print a list of selected files 
    with full path names.
    """
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.setWindowTitle("Hierarchical Media File Scanner")
        self.setGeometry(100, 100, 800, 600) # x, y, width, height

        # --- Define Media Extensions ---
        self.IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
        self.VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv')
        self.MEDIA_EXTENSIONS = self.IMAGE_EXTENSIONS + self.VIDEO_EXTENSIONS

        # Create the main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Create the "central" content widget
        self.content_widget = QWidget()
        layout = QVBoxLayout(self.content_widget) # Layout for the content widget
        self.main_layout.addWidget(self.content_widget)
     
        # --- Central Widget and Layout ---
        # central_widget = QWidget()
        # self.setCentralWidget(central_widget)
        # layout = QVBoxLayout(central_widget)

        # --- QTreeView for displaying results ---
        self.tree_view = QTreeView()
        self.tree_view.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Name', 'Size (KB)'])
        self.tree_view.setModel(self.model)
        
        # Connect the selectionChanged signal
        self.tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # --- UI Polish: Adjust column widths ---
        # Enable interactive resizing for all columns
        header = self.tree_view.header()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        # Make the first column (File Name) stretch to fill available space
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        # Resize the second column (Size) to fit its contents
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        # Set uniform row heights for a cleaner look
        self.tree_view.setUniformRowHeights(True)

        # --- Button to open folder dialog ---
        self.button_panel = QWidget() # Container for buttons
        self.button_panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button_layout = QHBoxLayout(self.button_panel)

        # --- Buttons ---
        self.new_button = QPushButton("New")   
        self.open_button = QPushButton("Open")  
        self.save_button = QPushButton("Save")
        self.new_button.clicked.connect(self.open_folder_dialog)

        # Add buttons to the button layout
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.save_button)


        # --- Add widgets to the layout ---
        layout.addWidget(self.tree_view)
        layout.addWidget(self.button_panel)

    def on_selection_changed(self):
        """
        Slot to handle the selectionChanged event.
        Print the full paths of all currently selected media files.
        """

        # Get all currently selected items
        all_selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        file_list = []
        if all_selected_indexes:
            print("All currently selected items:")
            for index in all_selected_indexes:
                if self.model.data(index, MyCustomDataRole):
                    file_list.append(self.model.data(index, MyCustomDataRole))
                    # print(f"  - {self.model.data(index, MyCustomDataRole)}")

        print(file_list)

    def open_folder_dialog(self):
        """
        Opens a dialog to select a folder and initiates the scan if a folder is chosen.
        """
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        
        # Proceed only if the user selected a folder (didn't cancel)
        if folder_path:
            self.setWindowTitle(f"Hierarchical Media Scanner - {folder_path}")
            self.scan_folder(folder_path)

    def scan_folder(self, folder_path):
        """
        Recursively scans the given folder for media files and populates the QTreeView.
        """
        # Clear previous results
        self.model.removeRows(0, self.model.rowCount())
        root_node = self.model.invisibleRootItem()

        # Create a visible top-level item for the folder that was selected
        top_folder_name = os.path.basename(folder_path)
        top_level_item = QStandardItem(f"📁 {top_folder_name}")
        top_level_item.setEditable(False)
        root_node.appendRow(top_level_item)

        # A dictionary to map folder paths to their QStandardItem in the tree.
        # Initialize it with the top-level folder we just created.
        folder_items = {folder_path: top_level_item}

        # Use os.walk to traverse the directory tree top-down
        for root, dirs, files in os.walk(folder_path):
            # Find the parent item for the current 'root' directory from our dictionary.
            parent_item = folder_items.get(root)
            if parent_item is None:
                continue

            # Add sub-folders to the tree
            # We sort them to ensure a consistent order
            for dir_name in sorted(dirs):
                full_dir_path = os.path.join(root, dir_name)
                # Create a QStandardItem for the folder
                folder_item = QStandardItem(f"📁 {dir_name}")
                folder_item.setEditable(False)
                
                # Add the folder item as a child of its parent
                parent_item.appendRow(folder_item)
                
                # Store this new folder item in our dictionary for its children
                folder_items[full_dir_path] = folder_item

            # Add media files to the tree
            for filename in sorted(files):
                if filename.lower().endswith(self.MEDIA_EXTENSIONS):
                    full_path = os.path.join(root, filename)
                    
                    try:
                        # Get file size in bytes and convert to kilobytes
                        size_bytes = os.path.getsize(full_path)
                        size_kb = size_bytes / 1024
                        
                        # Create items for the name and size columns
                        item_name = QStandardItem(f"📄 {filename}")
                        item_size = QStandardItem(f"{size_kb:.2f}")
                        
                        # custom data role
                        item_name.setData(full_path, MyCustomDataRole)

                        item_name.setEditable(False)
                        item_size.setEditable(False)
                        
                        # Add the file as a new row under its parent folder
                        parent_item.appendRow([item_name, item_size])

                    except OSError as e:
                        print(f"Error accessing {full_path}: {e}")
        
        # Automatically expand the top-level item if it exists
        if self.model.rowCount() > 0:
             self.tree_view.expand(self.model.index(0, 0))


# --- Main execution block ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MediaScannerApp()
    window.show()
    sys.exit(app.exec())
