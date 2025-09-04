from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import QItemSelection, QModelIndex
import sys

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 QTreeView Selection Changed")
        self.setGeometry(100, 100, 400, 300)

        self.tree_view = QTreeView(self)
        self.setCentralWidget(self.tree_view)

        self.model = QStandardItemModel()
        self.tree_view.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.model.setHorizontalHeaderLabels(["Item"])
        self.tree_view.setModel(self.model)

        # Add some items to the tree
        parent_item = QStandardItem("Parent 1")
        self.model.appendRow(parent_item)
        parent_item.appendRow(QStandardItem("Child 1.1"))
        parent_item.appendRow(QStandardItem("Child 1.2"))

        parent_item_2 = QStandardItem("Parent 2")
        self.model.appendRow(parent_item_2)
        parent_item_2.appendRow(QStandardItem("Child 2.1"))

        # Connect the selectionChanged signal
        self.tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)

    def on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        """
        Slot to handle the selectionChanged event.
        :param selected: A QItemSelection containing newly selected items.
        :param deselected: A QItemSelection containing newly deselected items.
        """
        print("Selection changed!")
        
        if selected.indexes():
            print("Selected items:")
            for index in selected.indexes():
                item = self.model.itemFromIndex(index)
                print(f"  - {item.text()}")

        if deselected.indexes():
            print("Deselected items:")
            for index in deselected.indexes():
                item = self.model.itemFromIndex(index)
                print(f"  - {item.text()}")

        # You can also get all currently selected items directly
        all_selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        if all_selected_indexes:
            print("All currently selected items:")
            for index in all_selected_indexes:
                item = self.model.itemFromIndex(index)
                print(f"  - {item.text()}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
