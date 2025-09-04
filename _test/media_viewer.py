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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # --- Option 1: Use your own files ---
    # Comment out the dummy file creation and uncomment this section.
    # Replace the file paths with paths to your own media.
    my_media = ['/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_184038458.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_184136694.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_185442125.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_185838674.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_185918970.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_190229165.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_190258886.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_190410136.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_190853606.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_193006814.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_193014505.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_193658737.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_193701897.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_193939572.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_194135525.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_194140486.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_194225249.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_194227225.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_194639966.NIGHT.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_194807309.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_194813477.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_195148231.NIGHT.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_195244222.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_195408011.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_195523770.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_195646939.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202245883.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202403791.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202407142.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202411022.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202416137.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202420554.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202450035.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202453078.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202628967.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202641578.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202719916.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202818426.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202819094.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202819997.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_202822233.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_203037249.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_203225879.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_203229115.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_203231493.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_203234304.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_203358504.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_203415207.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_203622810.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_203632120.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_204013590.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_210017533.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_210046894.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_210214781.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_210217519.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_210714705.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_210720216.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_212419177.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_215610639.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_215901464.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08-05/PXL_20250805_222315737.PORTRAIT.jpg', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250804_174959675.mp4', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250804_180629537.mp4', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250804_181815575.mp4', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_202643083.mp4', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_202727024.mp4', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_203346845.mp4', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_214421175.mp4', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_214428748.mp4', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_214440453.mp4', '/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_234716743.mp4']

    viewer = MediaViewer(my_media)
    viewer.show()

    sys.exit(app.exec())
    