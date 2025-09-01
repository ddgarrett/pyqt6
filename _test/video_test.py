from PyQt6.QtCore import QSize, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player")

        self.viewer = QVideoWidget()
        self.viewer.setMinimumSize(QSize(800, 400))
        self.player = QMediaPlayer()
        self.audioOutput = QAudioOutput()  # Keep a reference to QAudioOutput
        self.player.setAudioOutput(self.audioOutput)

        self.loadVideoBtn = QPushButton("Open video file...")
        self.loadVideoBtn.pressed.connect(self.openVideFile)

        layout = QVBoxLayout()
        layout.addWidget(self.viewer)
        layout.addWidget(self.loadVideoBtn)
        self.setLayout(layout)

    def openVideFile(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            caption="Open video file",
            filter="MP4 Video (*.mp4)",
        )

        if filename:
            video = QUrl(filename)
            self.player.setSource(video)
            self.player.setVideoOutput(self.viewer)
            self.player.play()

app = QApplication([])
window = Window()
window.show()
app.exec()