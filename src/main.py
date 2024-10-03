import sys
import yt_dlp
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon


class DownloadThread(QThread):
    update_progress = pyqtSignal(float)
    finished = pyqtSignal()

    def __init__(self, url, quality, output_folder):
        super().__init__()
        self.url = url
        self.quality = quality
        self.output_folder = output_folder

    def run(self):
        ydl_opts = {
            'format': self.quality if self.quality != 'best' else 'bestvideo+bestaudio/best',
            'outtmpl': f'{self.output_folder}/%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook]
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished.emit()
        except Exception as e:
            self.finished.emit()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percentage = float(d['_percent_str'].strip().replace('%', ''))
            self.update_progress.emit(percentage)


class FuturisticDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Determine the correct path for the icon
        if getattr(sys, 'frozen', False):
            # If the application is running as a bundled executable
            icon_path = os.path.join(sys._MEIPASS, 'youtube.png')
        else:
            # If running in a normal Python environment
            icon_path = 'youtube.png'

        # Set the application icon
        self.setWindowIcon(QIcon(icon_path))  # Use the determined icon path

        self.setWindowTitle('YouTube Video/Stream Downloader - Made by Fenix')
        self.setGeometry(100, 100, 600, 400)
        
        # Layout
        layout = QGridLayout()
        
        # Global styling for glassmorphism and neon colors
        self.setStyleSheet(
    """
    QWidget {
        background-color: #1e1e2f;
        font-family: 'Poppins', sans-serif;
        color: white;
    }
    QLabel {
        font-size: "14px";
        color: #a9a9b3;
    }
    QLineEdit {
        padding: 12px;
        font-size: "14px";
        border-radius: 15px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
    }
    QPushButton {
        padding: 15px;
        font-size: "14px";
        border-radius: 20px;
        background-color: #3498db;
        color: white;
        transition: 0.2s;
    }
    QPushButton:hover {
        background-color: #3ab5f7;
        color: #fff;
        border-radius: 22px;
    }
    QComboBox {
        padding: 10px;
        font-size: "14px";
        border-radius: 15px;
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    QProgressBar {
        border-radius: 15px;
        text-align: center;
        color: white;
        background-color: rgba(255, 255, 255, 0.1);
        height: 30px;
    }
    QProgressBar::chunk {
        background-color: #1abc9c;
        border-radius: 15px;
    }
    """
)

        # URL
        self.url_label = QLabel("Enter YouTube Live Stream URL:")
        layout.addWidget(self.url_label, 0, 0)

        self.url_input = QLineEdit()
        layout.addWidget(self.url_input, 0, 1)

        # Quality
        self.quality_label = QLabel("Select Video Quality:")
        layout.addWidget(self.quality_label, 1, 0)

        self.quality_dropdown = QComboBox()
        self.quality_dropdown.addItems(["Best Available", "1080p", "720p", "480p", "360p", "audio"])
        layout.addWidget(self.quality_dropdown, 1, 1)

        # Output
        self.output_button = QPushButton("Choose Output Folder")
        self.output_button.setIcon(QIcon.fromTheme("folder"))
        self.output_button.clicked.connect(self.choose_output_folder)
        layout.addWidget(self.output_button, 2, 0, 1, 2)

        # Folder label
        self.output_folder_label = QLabel("No folder selected")
        layout.addWidget(self.output_folder_label, 3, 0, 1, 2)

        # Download Button
        self.download_button = QPushButton("Download Stream")
        self.download_button.setIcon(QIcon.fromTheme("download"))
        self.download_button.clicked.connect(self.download_video)
        layout.addWidget(self.download_button, 4, 0, 1, 2)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar, 5, 0, 1, 2)

        # Status
        self.status_label = QLabel("")
        layout.addWidget(self.status_label, 6, 0, 1, 2)

        # Branding
        self.brand_label = QLabel("Made by Fen1x")
        self.brand_label.setStyleSheet("font-size: 12px; color: #a9a9b3; text-align: center;")
        layout.addWidget(self.brand_label, 7, 0, 1, 2)

        self.setLayout(layout)

    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_folder_label.setText(f"Output folder: {folder}")

    def download_video(self):
        url = self.url_input.text()
        quality = self.quality_dropdown.currentText()
        output_folder = self.output_folder

        if not url:
            QMessageBox.critical(self, "Error", "Please enter a YouTube URL")
            return

        if not output_folder:
            QMessageBox.critical(self, "Error", "Please select an output folder")
            return

        self.status_label.setText("Downloading...")

        # Start the download thread
        self.thread = DownloadThread(url, quality, output_folder)
        self.thread.update_progress.connect(self.update_progress)
        self.thread.finished.connect(self.download_complete)
        self.thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(int(progress))

    def download_complete(self):
        QMessageBox.information(self, "Download Complete", "The live stream has been downloaded successfully!")
        self.status_label.setText("Download complete.")
        self.progress_bar.setValue(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader_app = FuturisticDownloaderApp()
    downloader_app.show()
    sys.exit(app.exec_())
