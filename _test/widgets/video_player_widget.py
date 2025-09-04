"""
    Widget for playing video files using QMediaPlayer.

    To use, create an instance passing the full path name of the video file.
"""

import os

from PyQt6.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QSlider, QStyle
)

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaMetaData
from PyQt6.QtMultimediaWidgets import QVideoWidget


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

        # Create QAudioOutput and set it on the media player
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

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

        # show metadata
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
 
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

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.print_media_metadata(self.media_player.metaData())

    def print_media_metadata(self, metadata):

        '''
        if metadata.isEmpty():
            print("No metadata available for this media file.")
            return
        '''

        print("--- QMediaMetaData ---")
        
        # Iterate through all available metadata keys
        for key in QMediaMetaData.Key:
            value = metadata.value(key)
            
            # Check if the value is valid before printing
            if value:
                # The value is a QVariant, which is automatically converted
                # to a Python type, so you can print it directly
                print(f"{key.name}: {value}")

        print("----------------------")