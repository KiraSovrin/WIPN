import sys
import time
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSlider
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import requests
from io import BytesIO
import ctypes  # For Windows API calls

# Load secrets from .env file
load_dotenv()

# Fetch credentials from environment variables
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# Initialize Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-read-currently-playing user-modify-playback-state user-read-playback-state"
))

class SpotifyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Now Playing")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        # For dragging
        self.dragging = False
        self.drag_position = QPoint()

        # Apply Windows glass effect
        self.apply_glass_effect()

        # Layouts
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Close Button
        close_button = QPushButton("❌")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("color: white; background-color: transparent; border: none;")
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Album Art
        self.album_label = QLabel()
        self.album_label.setFixedSize(100, 100)
        self.album_label.setStyleSheet("border-radius: 8px;")
        main_layout.addWidget(self.album_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Song and Artist Labels
        self.song_label = QLabel("Fetching current song...")
        self.song_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.song_label.setStyleSheet("color: white;")
        self.song_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.song_label)

        self.artist_label = QLabel()
        self.artist_label.setFont(QFont("Arial", 10))
        self.artist_label.setStyleSheet("color: white;")
        self.artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.artist_label)

        # Playback Controls
        control_layout = QHBoxLayout()
        self.prev_button = QPushButton("⏮")
        self.play_pause_button = QPushButton("⏯")
        self.next_button = QPushButton("⏭")

        for btn in [self.prev_button, self.play_pause_button, self.next_button]:
            btn.setStyleSheet("color: white; background-color: transparent; border: none;")
            btn.setFixedSize(30, 30)

        self.prev_button.clicked.connect(lambda: sp.previous_track())
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.next_button.clicked.connect(lambda: sp.next_track())

        control_layout.addWidget(self.prev_button)
        control_layout.addWidget(self.play_pause_button)
        control_layout.addWidget(self.next_button)
        main_layout.addLayout(control_layout)

        # Track Progress
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setStyleSheet("QSlider::handle { background-color: white; }")
        self.progress_slider.sliderReleased.connect(self.seek_track)
        main_layout.addWidget(self.progress_slider)

        self.setLayout(main_layout)

        # Update song info every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_song_info)
        self.timer.start(1000)
        self.update_song_info()

    def apply_glass_effect(self):
        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [("AccentState", ctypes.c_int),
                        ("AccentFlags", ctypes.c_int),
                        ("GradientColor", ctypes.c_int),
                        ("AnimationId", ctypes.c_int)]

        class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
            _fields_ = [("Attribute", ctypes.c_int),
                        ("Data", ctypes.POINTER(ACCENT_POLICY)),
                        ("SizeOfData", ctypes.c_size_t)]

        accent = ACCENT_POLICY()
        accent.AccentState = 3  # ACCENT_ENABLE_BLURBEHIND (3) for glass effect
        accent.GradientColor = 0xAAFFFFFF  # Semi-transparent white

        accent_ptr = ctypes.pointer(accent)

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19  # WCA_ACCENT_POLICY (19)
        data.Data = accent_ptr
        data.SizeOfData = ctypes.sizeof(accent)

        hwnd = int(self.winId())
        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))

    def update_song_info(self):
        try:
            current_track = sp.current_user_playing_track()
            if current_track and current_track['is_playing']:
                song_name = current_track['item']['name']
                artist_name = ', '.join([artist['name'] for artist in current_track['item']['artists']])
                album_art_url = current_track['item']['album']['images'][1]['url']

                self.song_label.setText(song_name)
                self.artist_label.setText(f"by {artist_name}")

                album_data = requests.get(album_art_url).content
                pixmap = QPixmap()
                pixmap.loadFromData(album_data)
                self.album_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))

                self.play_pause_button.setText("⏸" if current_track['is_playing'] else "⏯")

                # Update progress slider
                progress_ms = current_track['progress_ms']
                duration_ms = current_track['item']['duration_ms']
                self.progress_slider.setMaximum(duration_ms)
                self.progress_slider.setValue(progress_ms)
            else:
                self.song_label.setText("No song playing")
                self.artist_label.setText("")
                self.progress_slider.setValue(0)
        except Exception as e:
            self.song_label.setText("Error fetching song")
            self.artist_label.setText(str(e))

    def toggle_play_pause(self):
        current_playback = sp.current_playback()
        if current_playback and current_playback['is_playing']:
            sp.pause_playback()
        else:
            sp.start_playback()

    def seek_track(self):
        # Seek to the selected position in the track
        sp.seek_track(self.progress_slider.value())

    # Mouse Press Event (For Dragging)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.pos()
            event.accept()

    # Mouse Move Event (For Dragging)
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.pos() - self.drag_position)
            event.accept()

    # Mouse Release Event (Stop Dragging)
    def mouseReleaseEvent(self, event):
        self.dragging = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SpotifyWidget()
    widget.show()
    sys.exit(app.exec())
