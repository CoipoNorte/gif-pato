# main.py

import sys
import os
import threading
import speech_recognition as sr
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QPoint, QUrl, pyqtSignal, QTimer
)
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QLineEdit, QHBoxLayout, QVBoxLayout, QToolButton
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(e)


class DuckWidget(ClickableLabel):
    def __init__(self, gifs_folder):
        super().__init__(alignment=Qt.AlignCenter)
        self.gifs = sorted(
            os.path.join(gifs_folder, f)
            for f in os.listdir(gifs_folder)
            if f.lower().endswith('.gif')
        )
        if not self.gifs:
            raise FileNotFoundError(f"No GIFs en '{gifs_folder}'")
        self.idx = 0
        self.movie = QMovie(self.gifs[self.idx])
        self.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()

        # Corregir posición
        self._base_pos = None
        self._anim = QPropertyAnimation(self, b"pos", self)
        self._anim.setDuration(300)
        self._anim.finished.connect(self._reset_pos)

    def next_duck(self):
        self.movie.stop()
        self.idx = (self.idx + 1) % len(self.gifs)
        self.movie.setFileName(self.gifs[self.idx])
        self.movie.start()
        self.movie.stop()

    def quack_anim(self):
        if self._base_pos is None:
            self._base_pos = self.pos()
        self._anim.stop()
        self._anim.setStartValue(self._base_pos)
        self._anim.setKeyValueAt(0.5, self._base_pos + QPoint(0, -15))
        self._anim.setEndValue(self._base_pos)
        self._anim.start()

    def _reset_pos(self):
        if self._base_pos is not None:
            self.move(self._base_pos)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pato UwU")
        self.resize(360, 480)

        # Media player para MP3
        self.player = QMediaPlayer(self)
        self.player.mediaStatusChanged.connect(self._on_media_status)

        # Rutas
        self.sound = os.path.abspath("sounds/pato.mp3")
        icons = "icons"

        # Widgets
        self.duck = DuckWidget("ducks")
        self.duck.clicked.connect(self._on_duck_clicked)

        self.log = QLabel("", alignment=Qt.AlignCenter)
        self.log.setObjectName("log")

        self.input = QLineEdit()
        self.input.setPlaceholderText("Escribe tu explicación…")
        self.input.returnPressed.connect(self._on_text_enter)

        btns = QHBoxLayout()
        self.btn_mic = QToolButton()
        self.btn_mic.setIcon(QIcon(os.path.join(icons, "micro.png")))
        self.btn_mic.clicked.connect(self._on_mic_click)
        self.btn_next = QToolButton()
        self.btn_next.setIcon(QIcon(os.path.join(icons, "pato.png")))
        self.btn_next.clicked.connect(self.duck.next_duck)
        btns.addWidget(self.btn_mic)
        btns.addStretch()
        btns.addWidget(self.btn_next)

        # Layout principal
        main = QVBoxLayout()
        main.addWidget(self.duck, stretch=1)
        main.addWidget(self.log)
        main.addWidget(self.input)
        main.addLayout(btns)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(15)
        container = QWidget()
        container.setLayout(main)
        self.setCentralWidget(container)

        # Estilos modernos
        self.setStyleSheet("""
            QMainWindow { background: #f0f2f5; }
            QLineEdit {
                padding: 8px; border: 1px solid #ccc;
                border-radius: 12px; background: white;
            }
            QToolButton {
                width: 40px; height: 40px;
                border: none; background: #ffffff;
                border-radius: 20px;
            }
            QToolButton:hover { background: #e1e5ea; }
            QLabel#log { color: #555; font-size: 14px; min-height: 24px; }
        """)

    def _play_quack(self):
        if os.path.exists(self.sound):
            url = QUrl.fromLocalFile(self.sound)
            self.player.setMedia(QMediaContent(url))
            self.player.setVolume(100)
            self.player.play()
        self.duck.movie.start()
        self.duck.quack_anim()

    def _on_media_status(self, status):
        from PyQt5.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.EndOfMedia:
            self.duck.movie.stop()

    def _on_text_enter(self):
        txt = self.input.text().strip()
        if not txt:
            self.log.setText("<font color='#d64'>¡Escribe algo!</font>")
            return
        self.log.setText(f"Tú: {txt}")
        self.input.clear()
        self._play_quack()

    def _on_mic_click(self):
        self.btn_mic.setEnabled(False)
        self.log.setText("🎤 escuchando…")
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        r = sr.Recognizer()
        with sr.Microphone() as src:
            r.adjust_for_ambient_noise(src, duration=1)
            try:
                aud = r.listen(src, timeout=5)
                txt = r.recognize_google(aud, language="es-ES")
            except Exception as e:
                txt = f"[{e.__class__.__name__}]"

        # Actualizar UI en hilo principal con QTimer
        def fin():
            self.log.setText(f"Tú (mic): {txt}")
            self.btn_mic.setEnabled(True)
            self._play_quack()

        QTimer.singleShot(0, fin)

    def _on_duck_clicked(self):
        self.log.setText("¡Cuak!")
        self._play_quack()


if __name__ == "__main__":
    # pip install PyQt5 SpeechRecognition PyAudio
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
