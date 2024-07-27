import sys
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty, QRect, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QBrush
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel

class SwitchWidget(QWidget):
    
    """
    A custom switch widget that toggles between on and off states with animation.

    Attributes:
        toggled (pyqtSignal): Signal emitted when the switch is toggled.
    """

    toggled = pyqtSignal(bool)

    def __init__(self, width=60, bg_color="#777", circle_color="#DDD", 
                 active_color="#00BCFF"):
        
        """
        Initializes the SwitchWidget.

        Args:
            width (int): The width of the switch.
            bg_color (str): The background color of the switch.
            circle_color (str): The color of the circle.
            active_color (str): The color when the switch is active.
        """

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

        """
        Handles the paint event to draw the switch.

        Args:
            e (QPaintEvent): The paint event.
        """

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
        p.drawRoundedRect(0, 0, rect.width(), self.height(), 
                          self.height() / 2, self.height() / 2)

        # Draw circle
        p.setBrush(QBrush(QColor(self._circle_color)))
        p.drawEllipse(self._circle_position, 3, 22, 22)

        p.end()

    @pyqtProperty(int)
    def circlePosition(self):

        """
        Gets the current circle position.
        
        Returns:
            int: The current circle position.
        """

        return self._circle_position

    @circlePosition.setter
    def circlePosition(self, pos):

        """
        Sets the circle position and updates the widget.

        Args:
            pos (int): The new circle position.
        """

        self._circle_position = pos
        self.update()

    def mousePressEvent(self, event):

        """
        Handles the mouse press event to toggle the switch.

        Args:
            event (QMouseEvent): The mouse event.
        """

        self._checked = not self._checked
        self.toggled.emit(self._checked)  # Emit the toggled signal
        self.start_animation()
        self.update()

    def start_animation(self):

        """
        Starts the animation for the switch toggle.
        """

        start_pos = 3 if self._checked else self.width() - 25
        end_pos = self.width() - 25 if self._checked else 3
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.start()

    def isChecked(self):
        
        """
        Checks if the switch is in the on state.

        Returns:
            bool: True if the switch is on, False otherwise.
        """

        return self._checked

# Test the widget
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    switch = SwitchWidget(bg_color="green", active_color="red")
    switch.toggled.connect(lambda checked: print(f"Switch toggled: {checked}"))

    layout.addWidget(switch)
    window.setCentralWidget(central_widget)
    window.show()
    sys.exit(app.exec())
