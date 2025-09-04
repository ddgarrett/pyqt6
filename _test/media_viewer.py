import sys
import os
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QSlider, QStyle
)
from PyQt6.QtGui import QPixmap, QImage, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QUrl
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget

# --- Constants for file type detection ---
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv')
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')


class VideoPlayerWindow(QWidget):
    """
    A new window for playing a selected video file using QMediaPlayer.
    """
    def __init__(self, video_path):
        super().__init__()
        self.setWindowTitle(f"Video Player - {os.path.basename(video_path)}")
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet("background-color: black;")

        # --- Media Player and Video Widget ---
        self.media_player = QMediaPlayer(self)
        video_widget = QVideoWidget()
        self.media_player.setVideoOutput(video_widget)
        self.media_player.setSource(QUrl.fromLocalFile(video_path))

        # --- Playback Controls ---
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)

        # --- Layout ---
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.addWidget(self.play_pause_btn)
        control_layout.addWidget(self.seek_slider)

        main_layout = QVBoxLayout()
        main_layout.addWidget(video_widget)
        main_layout.addLayout(control_layout)
        self.setLayout(main_layout)

        # --- Connect Signals ---
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.media_player.playbackStateChanged.connect(self.update_play_button_icon)
        self.media_player.durationChanged.connect(self.update_slider_range)
        self.media_player.positionChanged.connect(self.update_slider_position)
        self.seek_slider.sliderMoved.connect(self.set_player_position)

        # Start playing immediately
        self.media_player.play()

    def toggle_play_pause(self):
        """Plays or pauses the video depending on its current state."""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def update_play_button_icon(self, state):
        """Changes the play/pause button icon based on the player's state."""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def update_slider_range(self, duration):
        """Sets the maximum value of the seek slider."""
        self.seek_slider.setRange(0, duration)

    def update_slider_position(self, position):
        """Updates the slider's handle position as the video plays."""
        self.seek_slider.setValue(position)

    def set_player_position(self, position):
        """Seeks the video to the position selected on the slider."""
        self.media_player.setPosition(position)
    
    def closeEvent(self, event):
        """Stops the media player when the window is closed."""
        self.media_player.stop()
        super().closeEvent(event)


class ClickableMediaLabel(QLabel):
    """A custom QLabel that emits a signal on a double-click event."""
    doubleClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Overrides the default event to emit our custom signal."""
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)


class MediaViewer(QMainWindow):
    """The main window for viewing a list of images and video thumbnails."""
    def __init__(self, media_files: list):
        super().__init__()
        if not media_files:
            raise ValueError("The list of media files cannot be empty.")

        self.media_files = media_files
        self.current_index = 0
        self.is_current_media_video = False
        self.original_pixmap = QPixmap()
        self.player_windows = [] # Keep references to open player windows

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
        main_layout.addWidget(self.media_label, stretch=1)

        # --- Navigation Buttons ---
        button_layout = QHBoxLayout()
        btn_first, btn_prev = QPushButton("<< First"), QPushButton("< Previous")
        btn_next, btn_last = QPushButton("Next >"), QPushButton("Last >>")
        
        for btn in [btn_first, btn_prev, btn_next, btn_last]:
            button_layout.addWidget(btn)

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
        qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(qt_image)

    def update_media_display(self):
        """
        Scales the original pixmap to fit the label's current size while
        maintaining aspect ratio and using smooth transformation.
        """
        if self.original_pixmap.isNull():
            self.media_label.setPixmap(QPixmap())
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
        """
        If the current item is a video, this opens a new VideoPlayerWindow
        to play the video file.
        """
        if self.is_current_media_video:
            filepath = self.media_files[self.current_index]
            print(f"Opening video player for: {filepath}")
            # Create the new window and show it
            player_window = VideoPlayerWindow(filepath)
            # Add to list to prevent garbage collection
            self.player_windows.append(player_window)
            player_window.show()

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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # --- Option 1: Use your own files ---
    # Comment out the dummy file creation and uncomment this section.
    # Replace the file paths with paths to your own media.
    my_media = ['/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_172414212.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_172418744.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_213533766.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_214433246.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_214524604.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_214642306.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_214646433.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_214650850.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_214719284.PANO.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_214850022.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_215515534.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_215518578.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_220135158.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_222228575.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_222233295.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_222236175.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_222356439.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_222506245.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_222513229.NIGHT.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_222531590.PANO.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_222638000.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_222644459.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_222649117.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_234429962.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_234455753.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_234459020.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250803_234506240.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250804_003349773.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250804_013031680.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250804_021527737.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250804_021531759.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250804_021547263.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08-03/PXL_20250804_021559371.jpg', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250804_174959675.mp4', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250804_180629537.mp4', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250804_181815575.mp4', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_202643083.mp4', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_202727024.mp4', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_203346845.mp4', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_214421175.mp4', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_214428748.mp4', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_214440453.mp4', '/Volumes/T7/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_234716743.mp4']
    viewer = MediaViewer(my_media)
    viewer.show()

    # --- Option 2: Use auto-generated dummy files ---
    # This will run by default.
    '''
    dummy_media_list = create_dummy_files()
    if dummy_media_list:
        viewer = MediaViewer(dummy_media_list)
        viewer.show()
    else:
        # If file creation fails, exit gracefully.
        sys.exit(1)
    '''
    sys.exit(app.exec())
    