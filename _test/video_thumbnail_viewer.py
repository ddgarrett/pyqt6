import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QFileDialog,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QPolygon, QPen, QBrush
from PyQt6.QtCore import Qt, QPoint

"""
    create a python qt6 program that allows selecting a video 
    then shows the first frame of the video as an image with a light gray play icon on it. 
    Resize the resulting image to fit the current window size.

"""

class VideoThumbnailViewer(QMainWindow):
    """
    A window that displays the first frame of a selected video
    with a play icon overlay. The image resizes with the window.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Thumbnail Viewer")
        self.setGeometry(100, 100, 800, 600)

        # This will hold the original, full-resolution pixmap with the overlay
        self.original_pixmap = None

        # Set up the central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Image display label
        self.image_label = QLabel("Click anywhere to select a video", self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(
            """
            QLabel {
                color: #aaa;
                font-size: 24px;
                border: 2px dashed #ccc;
                border-radius: 10px;
            }
        """
        )
        layout.addWidget(self.image_label)
        self.setMinimumSize(400, 300)

    def mousePressEvent(self, event):
        """Handle clicks to open the file dialog."""
        self.open_video_file()

    def open_video_file(self):
        """Open a file dialog to select a video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)",
        )

        if file_path:
            self.process_video(file_path)

    def process_video(self, file_path):
        """
        Extracts the first frame from the video, converts it to a QPixmap,
        and draws the play icon overlay.
        """
        try:
            # Use OpenCV to capture the video
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                self.image_label.setText("Error: Could not open video file.")
                self.image_label.setStyleSheet("color: red; font-size: 18px;")
                return

            # Read the first frame
            ret, frame = cap.read()
            cap.release()

            if not ret:
                self.image_label.setText("Error: Could not read the first frame.")
                self.image_label.setStyleSheet("color: red; font-size: 18px;")
                return

            # Convert OpenCV's BGR format to RGB for Qt
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = rgb_frame.shape
            bytes_per_line = 3 * width

            # Create a QImage from the frame data
            q_image = QImage(
                rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
            )
            pixmap = QPixmap.fromImage(q_image)

            # Store the pixmap with the overlay for high-quality resizing
            self.original_pixmap = self.draw_play_icon(pixmap)
            
            # Remove the initial placeholder style
            self.image_label.setStyleSheet("")
            self.image_label.setText("")

            # Perform the initial display update
            self.update_image_display()

        except Exception as e:
            self.image_label.setText(f"An error occurred:\n{e}")
            self.image_label.setStyleSheet("color: red; font-size: 14px;")
            print(f"Error processing video: {e}")

    def draw_play_icon(self, pixmap):
        """
        Draws a semi-transparent light gray play icon in the center of the pixmap.
        """
        # Create a QPainter to draw on the pixmap
        painter = QPainter(pixmap)
        
        # Configure pen and brush for the icon
        pen = QPen(Qt.PenStyle.NoPen)
        brush = QBrush(QColor(200, 200, 200, 180)) # Light gray, semi-transparent
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate icon size and position (relative to pixmap size)
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()
        center_x, center_y = pixmap_width // 2, pixmap_height // 2
        
        # Make the icon size proportional to the image's smaller dimension
        icon_size = min(pixmap_width, pixmap_height) // 6

        # Define the points of the triangle (play button)
        p1 = QPoint(center_x - icon_size // 2, center_y - int(icon_size * 0.866 / 2))
        p2 = QPoint(center_x - icon_size // 2, center_y + int(icon_size * 0.866 / 2))
        p3 = QPoint(center_x + icon_size // 2, center_y)

        # Create a QPolygon from the points
        play_triangle = QPolygon([p1, p2, p3])
        
        # Draw the polygon on the pixmap
        painter.drawPolygon(play_triangle)
        
        # Finalize the drawing
        painter.end()
        
        return pixmap


    def resizeEvent(self, event):
        """
        Handles the window resize event to scale the image.
        """
        super().resizeEvent(event)
        self.update_image_display()

    def update_image_display(self):
        """
        Scales the original pixmap to fit the label's current size
        while maintaining aspect ratio.
        """
        if self.original_pixmap:
            # Scale the stored original pixmap for the best quality
            scaled_pixmap = self.original_pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)


def main():
    app = QApplication(sys.argv)
    viewer = VideoThumbnailViewer()
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
