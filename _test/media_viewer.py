import sys
import os
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
)
from PyQt6.QtGui import QPixmap, QImage, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QSize

# --- Constants for file type detection ---
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv')
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')


class ClickableMediaLabel(QLabel):
    """
    A custom QLabel subclass that emits a signal on a double-click event.
    This is used to detect when a user wants to interact with the displayed media.
    """
    doubleClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Overrides the default event to emit our custom signal."""
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)


class MediaViewer(QMainWindow):
    """
    A window for viewing a list of images and video thumbnails.
    """
    def __init__(self, media_files: list):
        super().__init__()

        if not media_files:
            raise ValueError("The list of media files cannot be empty.")

        self.media_files = media_files
        self.current_index = 0
        self.is_current_media_video = False
        self.original_pixmap = QPixmap() # Store the full-resolution loaded media

        self.setWindowTitle("Media Viewer")
        self.setMinimumSize(400, 300)
        self.resize(800, 600)

        # --- Main UI Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Media Display Label ---
        self.media_label = ClickableMediaLabel()
        self.media_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.media_label.setStyleSheet("background-color: black;")
        main_layout.addWidget(self.media_label, stretch=1) # The '1' allows it to grow

        # --- Navigation Buttons ---
        button_layout = QHBoxLayout()
        btn_first = QPushButton("<< First")
        btn_prev = QPushButton("< Previous")
        btn_next = QPushButton("Next >")
        btn_last = QPushButton("Last >>")

        # Add buttons to the button layout
        button_layout.addWidget(btn_first)
        button_layout.addWidget(btn_prev)
        button_layout.addStretch() # Adds space between button groups
        button_layout.addWidget(btn_next)
        button_layout.addWidget(btn_last)

        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)

        # --- Connect Signals to Slots ---
        btn_first.clicked.connect(self.go_to_first)
        btn_prev.clicked.connect(self.go_to_previous)
        btn_next.clicked.connect(self.go_to_next)
        btn_last.clicked.connect(self.go_to_last)
        self.media_label.doubleClicked.connect(self.handle_double_click)

        # Load the first media item
        self.load_current_media()

    def load_current_media(self):
        """Loads the media file at the current index into the pixmap."""
        filepath = self.media_files[self.current_index]
        filename = os.path.basename(filepath)

        if filepath.lower().endswith(IMAGE_EXTENSIONS):
            self.is_current_media_video = False
            self.original_pixmap = QPixmap(filepath)
            self.setWindowTitle(f"Media Viewer - Image: {filename}")

        elif filepath.lower().endswith(VIDEO_EXTENSIONS):
            self.is_current_media_video = True
            self.original_pixmap = self._get_video_frame(filepath)
            self.setWindowTitle(f"Media Viewer - Video: {filename} (First Frame)")

        else:
            # Handle unsupported file types by showing a blank pixmap
            self.is_current_media_video = False
            self.original_pixmap = QPixmap()
            print(f"Warning: Unsupported file type: {filename}")
            self.setWindowTitle(f"Media Viewer - Unsupported File: {filename}")

        self.update_media_display()

    def _get_video_frame(self, video_path: str) -> QPixmap:
        """
        Opens a video file, captures the first frame, and returns it as a QPixmap.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file {video_path}")
            return QPixmap() # Return an empty pixmap on failure

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print(f"Error: Could not read first frame from {video_path}")
            return QPixmap()

        # Convert OpenCV's BGR format to RGB for PyQt
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w

        # Create a QImage from the numpy array
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(qt_image)

    def update_media_display(self):
        """
        Scales the original pixmap to fit the label's current size while
        maintaining aspect ratio and using smooth transformation.
        """
        if self.original_pixmap.isNull():
            self.media_label.setPixmap(QPixmap()) # Clear the label if pixmap is invalid
            return

        # Scale the pixmap to fit the label, keeping aspect ratio
        scaled_pixmap = self.original_pixmap.scaled(
            self.media_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.media_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """
        This event is triggered whenever the window is resized. We use it
        to re-scale the displayed media.
        """
        self.update_media_display()
        super().resizeEvent(event)

    # --- Navigation Slot Methods ---

    def go_to_next(self):
        """Moves to the next item in the media list."""
        if self.current_index < len(self.media_files) - 1:
            self.current_index += 1
            self.load_current_media()

    def go_to_previous(self):
        """Moves to the previous item in the media list."""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_media()

    def go_to_first(self):
        """Jumps to the first item in the media list."""
        if self.current_index != 0:
            self.current_index = 0
            self.load_current_media()

    def go_to_last(self):
        """Jumps to the last item in the media list."""
        if self.current_index != len(self.media_files) - 1:
            self.current_index = len(self.media_files) - 1
            self.load_current_media()

    def handle_double_click(self):
        """Action to perform on double-click."""
        if self.is_current_media_video:
            filepath = self.media_files[self.current_index]
            print(f"Video file double-clicked: {filepath}")


# --- Helper functions to create dummy files for demonstration ---

def create_dummy_files(temp_dir="temp_media"):
    """Creates a temporary directory with a dummy image and video."""
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    print(f"Creating dummy media files in '{os.path.abspath(temp_dir)}'...")

    file_list = []

    # 1. Create a dummy image file
    try:
        image_path = os.path.join(temp_dir, "dummy_image.png")
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add a blue rectangle
        cv2.rectangle(image, (100, 100), (540, 380), (255, 100, 50), -1)
        cv2.putText(image, "Dummy Image", (160, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        cv2.imwrite(image_path, image)
        file_list.append(image_path)
        print(f"  - Created: {image_path}")
    except Exception as e:
        print(f"Could not create dummy image. Error: {e}")


    # 2. Create a dummy video file
    try:
        video_path = os.path.join(temp_dir, "dummy_video.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, 30.0, (640, 480))
        for i in range(90): # Create a 3-second video
            frame = np.full((480, 640, 3), (i * 2, 200 - i, 50 + i), dtype=np.uint8)
            text = f"Dummy Video Frame: {i+1}"
            cv2.putText(frame, text, (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            out.write(frame)
        out.release()
        file_list.append(video_path)
        print(f"  - Created: {video_path}")
    except Exception as e:
        print(f"Could not create dummy video. Error: {e}. Is 'opencv-python' installed?")

    # 3. Create another dummy image
    try:
        image_path_2 = os.path.join(temp_dir, "dummy_image_2.jpg")
        image2 = np.zeros((720, 1280, 3), dtype=np.uint8)
        # Add a green circle
        cv2.circle(image2, (640, 360), 300, (50, 200, 50), -1)
        cv2.putText(image2, "Another Image", (400, 380), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        cv2.imwrite(image_path_2, image2)
        file_list.append(image_path_2)
        print(f"  - Created: {image_path_2}")
    except Exception as e:
        print(f"Could not create second dummy image. Error: {e}")

    if not file_list:
        print("\nERROR: Failed to create any dummy media files.")
        print("Please ensure you have permissions to write to the directory and that opencv-python is installed correctly.")
        return None

    return file_list


# --- Main execution block ---

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # --- Option 1: Use your own files ---
    # Comment out the dummy file creation and uncomment this section.
    # Replace the file paths with paths to your own media.
    # my_media = [
    #     "/path/to/your/image.jpg",
    #     "/path/to/your/video.mp4",
    #     "/path/to/another/image.png"
    # ]
    # viewer = MediaViewer(my_media)
    # viewer.show()

    # --- Option 2: Use auto-generated dummy files ---
    # This will run by default.
    dummy_media_list = create_dummy_files()
    if dummy_media_list:
        viewer = MediaViewer(dummy_media_list)
        viewer.show()
    else:
        # If file creation fails, exit gracefully.
        sys.exit(1)

    sys.exit(app.exec())