from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout

class ThroughputWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.throughput_label = QLabel()
        self.throughput_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout()
        layout.addWidget(self.throughput_label)
        self.setLayout(layout)

        self.update_throughput(0)

    @pyqtSlot(int)
    def update_throughput(self, throughput: int):
        self.throughput_label.setText(f"Throughput: {throughput} tickets/hr")