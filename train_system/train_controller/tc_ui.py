
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QSlider, QPushButton, QTabWidget, QCheckBox)
from PyQt5.QtCore import Qt

class TrainEngineer(QWidget):
    def __init__(self):
        super().__init__()

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(QWidget(), "MBO")
        self.tabs.addTab(QWidget(), "CTC Office")
        self.tabs.addTab(QWidget(), "Track Model")
        self.tabs.addTab(QWidget(), "Train Model")
        self.tabs.addTab(QWidget(), "SW Track Controller")
        self.tabs.addTab(QWidget(), "HW Track Controller")
       
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        # Train Engineer label
        label = QLabel("Train Engineer:")
        main_layout.addWidget(label)

        # Dropdowns for Line and Train
        dropdown_layout = QHBoxLayout()
        self.line_dropdown = QComboBox()
        self.line_dropdown.addItem("Line")
        self.train_dropdown = QComboBox()
        self.train_dropdown.addItem("Train")
        dropdown_layout.addWidget(self.line_dropdown)
        dropdown_layout.addWidget(self.train_dropdown)
        main_layout.addLayout(dropdown_layout)

        # Sliders for Kp and Ki
        slider_layout = QVBoxLayout()
        self.kp_slider = QSlider(Qt.Horizontal)
        self.kp_slider.setMinimum(0)
        self.kp_slider.setMaximum(10)
        self.ki_slider = QSlider(Qt.Horizontal)
        self.ki_slider.setMinimum(0)
        self.ki_slider.setMaximum(10)
        slider_layout.addWidget(QLabel("Kp:"))
        slider_layout.addWidget(self.kp_slider)
        slider_layout.addWidget(QLabel("Ki:"))
        slider_layout.addWidget(self.ki_slider)
        main_layout.addLayout(slider_layout)

        # Start button
        self.start_button = QPushButton("START")
        main_layout.addWidget(self.start_button)

        # Test Bench switch
        switch_layout = QHBoxLayout()
        self.test_bench_label = QLabel("Test Bench")
        self.test_bench_switch = QCheckBox()
        self.test_bench_switch.setStyleSheet("QCheckBox::indicator { width: 40px; height: 20px; }")
        self.test_bench_switch.stateChanged.connect(self.toggle_test_bench)
        switch_layout.addWidget(self.test_bench_label)
        switch_layout.addWidget(self.test_bench_switch)
        main_layout.addLayout(switch_layout)

        self.setLayout(main_layout)

    def toggle_test_bench(self, state):
        if state == Qt.Checked:
            self.test_bench_switch.setStyleSheet("QCheckBox::indicator { width: 40px; height: 20px; background-color: green; }")
        else:
            self.test_bench_switch.setStyleSheet("QCheckBox::indicator { width: 40px; height: 20px; background-color: grey; }")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrainEngineer()
    window.show()
    sys.exit(app.exec_())