import sys
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty, QRect
from PyQt6.QtGui import QColor, QPainter, QBrush
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel

class SwitchWidget(QWidget):
    def __init__(
            self,
            width=60,
            bg_color="#777",
            circle_color="#DDD",
            active_color="#00BCFF"
        ):

        super().__init__()

        # Set default parameters
        self.setFixedSize(width, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Colors
        self._bg_color = bg_color
        self._circle_color = circle_color
        self._active_color = active_color

        # State
        self._checked = False

        # Animation
        self._circle_position = 3
        self.animation = QPropertyAnimation(self, b"circlePosition")
        self.animation.setDuration(300)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set as no pen
        p.setPen(Qt.PenStyle.NoPen)

        # Draw rectangle
        rect = QRect(0, 0, self.width(), self.height())

        # Draw BG
        if self._checked:
            p.setBrush(QColor(self._active_color))
        else:
            p.setBrush(QColor(self._bg_color))
        p.drawRoundedRect(0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2)

        # Draw circle
        p.setBrush(QBrush(QColor(self._circle_color)))
        p.drawEllipse(self._circle_position, 3, 22, 22)

        p.end()

    @pyqtProperty(int)
    def circlePosition(self):
        return self._circle_position

    @circlePosition.setter
    def circlePosition(self, pos):
        self._circle_position = pos
        self.update()

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self.start_animation()
        self.update()

    def start_animation(self):
        start_pos = 3 if self._checked else self.width() - 25
        end_pos = self.width() - 25 if self._checked else 3
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.start()
