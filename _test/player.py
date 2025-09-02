import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QStyle, QSlider, QLabel
)
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl

class VideoPlayer(QMainWindow):
    """A simple MP4 video player using PyQt6."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 MP4 Player")
        self.setGeometry(100, 100, 800, 600)

        # Create the central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # --- Media Player and Video Widget ---
        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        layout.addWidget(self.video_widget)

        # --- Controls ---
        controls_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        
        # --- Time Slider ---
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        controls_layout.addWidget(self.position_slider)

        # --- Time Label ---
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # --- Buttons ---
        # Open Button
        self.open_button = QPushButton()
        self.open_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self.open_button.setToolTip("Open Video File")
        
        # Rewind Button
        self.rewind_button = QPushButton()
        self.rewind_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        self.rewind_button.setToolTip("Rewind 5 seconds")

        # Play/Pause Button
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.setToolTip("Play")
        
        # Stop Button
        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_button.setToolTip("Stop")

        # Fast Forward Button
        self.ff_button = QPushButton()
        self.ff_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        self.ff_button.setToolTip("Fast Forward 5 seconds")
        
        # Add buttons to the layout
        buttons_layout.addWidget(self.open_button)
        buttons_layout.addWidget(self.rewind_button)
        buttons_layout.addWidget(self.play_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.ff_button)
        buttons_layout.addStretch() # Pushes the time label to the right
        buttons_layout.addWidget(self.time_label)
        
        controls_layout.addLayout(buttons_layout)
        layout.addLayout(controls_layout)

        # --- Connect Signals to Slots ---
        self.open_button.clicked.connect(self.open_file)
        self.play_button.clicked.connect(self.play_video)
        self.stop_button.clicked.connect(self.stop_video)
        self.rewind_button.clicked.connect(self.rewind_video)
        self.ff_button.clicked.connect(self.fast_forward_video)
        
        self.position_slider.sliderMoved.connect(self.set_position)
        
        self.media_player.playbackStateChanged.connect(self.update_play_button_icon)
        self.media_player.positionChanged.connect(self.update_slider_and_label)
        self.media_player.durationChanged.connect(self.update_slider_range)
        self.media_player.errorOccurred.connect(self.handle_error)
        
        # Set initial state of buttons
        self.set_controls_enabled(False)

    def set_controls_enabled(self, enabled):
        """Enable or disable media control buttons."""
        self.play_button.setEnabled(enabled)
        self.stop_button.setEnabled(enabled)
        self.rewind_button.setEnabled(enabled)
        self.ff_button.setEnabled(enabled)
        self.position_slider.setEnabled(enabled)

    def open_file(self):
        """Open a video file and set it as the media source."""
        # QFileDialog.getOpenFileUrl() is preferred for media content
        file_url, _ = QFileDialog.getOpenFileUrl(self, "Open MP4", filter="Video Files (*.mp4 *.avi *.mkv)")

        if file_url.isValid():
            self.media_player.setSource(file_url)
            self.set_controls_enabled(True)
            self.play_video() # Automatically play after opening

    def play_video(self):
        """Toggle between playing and pausing the video."""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def stop_video(self):
        """Stop the video and reset the position to the start."""
        self.media_player.stop()

    def rewind_video(self):
        """Rewind the video by 5000 milliseconds (5 seconds)."""
        current_position = self.media_player.position()
        new_position = max(0, current_position - 5000)
        self.media_player.setPosition(new_position)

    def fast_forward_video(self):
        """Fast forward the video by 5000 milliseconds (5 seconds)."""
        current_position = self.media_player.position()
        new_position = current_position + 5000
        # Ensure we don't go past the end
        if new_position < self.media_player.duration():
            self.media_player.setPosition(new_position)

    def set_position(self, position):
        """Set the media player's position based on the slider."""
        self.media_player.setPosition(position)

    def update_play_button_icon(self, state):
        """Update the play/pause button icon based on the playback state."""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.play_button.setToolTip("Pause")
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.play_button.setToolTip("Play")
            
    def update_slider_and_label(self, position):
        """Update the slider's value and the time label."""
        # Update slider (preventing signals from being emitted)
        self.position_slider.blockSignals(True)
        self.position_slider.setValue(position)
        self.position_slider.blockSignals(False)

        # Update time label
        duration = self.media_player.duration()
        self.time_label.setText(f"{self.format_time(position)} / {self.format_time(duration)}")

    def update_slider_range(self, duration):
        """Set the slider's maximum range when the media duration is known."""
        self.position_slider.setRange(0, duration)
        
    def format_time(self, milliseconds):
        """Format milliseconds into a MM:SS string."""
        seconds = int((milliseconds / 1000) % 60)
        minutes = int((milliseconds / (1000 * 60)) % 60)
        hours = int((milliseconds / (1000 * 60 * 60)) % 24)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def handle_error(self, error):
        """Handle media player errors."""
        print(f"Error: {self.media_player.errorString()}")
        self.set_controls_enabled(False)
        self.time_label.setText("Error")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())