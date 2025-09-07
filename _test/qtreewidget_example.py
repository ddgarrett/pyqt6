import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 QTreeWidget Example")
        self.setGeometry(100, 100, 400, 300)

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create the QTreeWidget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(2)  # Set two columns
        self.tree_widget.setHeaderLabels(["Category", "Description"]) # Set header labels

        # Sample Data
        data = {
            "Fruits": ["Apple", "Banana", "Orange"],
            "Vegetables": ["Carrot", "Broccoli", "Spinach"],
            "Dairy": ["Milk", "Cheese"]
        }

        # Populate the QTreeWidget
        for category, items in data.items():
            category_item = QTreeWidgetItem(self.tree_widget, [category, ""]) # Parent item
            for item_name in items:
                QTreeWidgetItem(category_item, [item_name, f"A delicious {item_name}"]) # Child item

        # Add the QTreeWidget to the layout
        layout.addWidget(self.tree_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    