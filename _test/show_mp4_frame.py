import sys
import cv2
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt

'''
    Requires Samsung T7 to be mounted
    
    NOTE: for pip install of cv2 had to code:
     % .venv/bin/python -m pip install opencv-python
'''

class VideoFrameViewer(QMainWindow):
    def __init__(self, video_path):
        super().__init__()
        self.setWindowTitle("MP4 First Frame Viewer")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.label = QLabel("Loading video thumbnail...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setScaledContents(True)  # Scale the image to fit the label size
        layout.addWidget(self.label)

        self.show_first_frame(video_path)

    def show_first_frame(self, video_path):
        # Open the video file
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            self.label.setText(f"Error: Could not open video file at '{video_path}'")
            return

        # Read the first frame
        ret, frame = cap.read()

        if ret:
            # The frame is in BGR format; convert it to RGB for PyQt
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            
            # Create a QImage from the RGB data
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Create a QPixmap from the QImage
            pixmap = QPixmap.fromImage(qt_image)
            
            # Set the pixmap on the QLabel
            self.label.setPixmap(pixmap)
        else:
            self.label.setText("Error: Could not read the first frame.")
            
        # Release the video capture object
        cap.release()

if __name__ == '__main__':
    # You need to install opencv-python: pip install opencv-python
    
    # Replace with the actual path to your MP4 file
    video_file = "/Volumes/T7/2025_pictures/2025_videos/PXL_20250611_203340430.mp4"

    app = QApplication(sys.argv)
    viewer = VideoFrameViewer(video_file)
    viewer.show()
    sys.exit(app.exec())
