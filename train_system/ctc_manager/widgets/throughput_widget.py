from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout

from train_system.common.palette import Colors
from train_system.common.line import Line

class ThroughputWidget(QWidget):

    def __init__(self, line: Line):
        super().__init__()

        """
        Initializes the ThroughputWidget.
        
        Args:
            line (Line): The line object containing track blocks.
        """

        self.line = line

        self.throughput_label = QLabel()
        self.throughput_label.setStyleSheet(
            f"color: {Colors.BLACK};"
            "font-size: 12pt;"
            "font-weight: 400;"
        )
        self.throughput_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout()
        layout.addWidget(self.throughput_label)
        self.setLayout(layout)

        self.handle_throughput_update(0)

    @pyqtSlot(int)
    def handle_throughput_update(self, throughput: int):

        """
        Updates the throughput label with the given throughput value.

        Args:
            throughput (int): The throughput value.
        """

        self.throughput_label.setText(f"Throughput: {throughput} tickets/hr")

    def set_line(self, line: Line):

        """
        Sets the line object for the widget.
        
        Args:
            line (Line): The line object containing track blocks.
        """
        
        self.line = line