import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QSlider, QPushButton, QTabWidget, QCheckBox, QSizePolicy)
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
        self.tabs.addTab(QWidget(), "SW Train Controller")
        self.tabs.addTab(QWidget(), "HW Train Controller")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        # Train Engineer label
        label = QLabel("Train Engineer:")
        label.setStyleSheet("font-size: 64;")
        main_layout.addWidget(label, alignment=Qt.AlignCenter)

        # Center container for inputs
        center_container = QWidget()
        center_container_layout = QVBoxLayout(center_container)
        center_container_layout.setAlignment(Qt.AlignCenter)
        center_container.setStyleSheet("background-color: white;")

        # Dropdowns for Line and Train
        dropdown_layout = QHBoxLayout()
        self.line_dropdown = QComboBox()
        self.line_dropdown.addItem("Line")
        self.line_dropdown.setStyleSheet("font-size: 32px;")
        self.train_dropdown = QComboBox()
        self.train_dropdown.addItem("Train")
        self.train_dropdown.setStyleSheet("font-size: 32px;")
        dropdown_layout.addWidget(self.line_dropdown)
        dropdown_layout.addWidget(self.train_dropdown)
        center_container_layout.addLayout(dropdown_layout)

        # Sliders for Kp and Ki
        slider_layout = QVBoxLayout()
        self.kp_slider = QSlider(Qt.Horizontal)
        self.kp_slider.setMinimum(0)
        self.kp_slider.setMaximum(10)
        self.ki_slider = QSlider(Qt.Horizontal)
        self.ki_slider.setMinimum(0)
        self.ki_slider.setMaximum(10)

        kp_label = QLabel("Kp:")
        kp_label.setStyleSheet("font-size: 32px;")
        ki_label = QLabel("Ki:")
        ki_label.setStyleSheet("font-size: 32px;")

        slider_layout.addWidget(kp_label)
        slider_layout.addWidget(self.kp_slider)
        slider_layout.addWidget(ki_label)
        slider_layout.addWidget(self.ki_slider)

        center_container_layout.addLayout(slider_layout)

        # Start button
        self.start_button = QPushButton("START")
        self.start_button.setStyleSheet("background-color: green; font-size: 32px; padding: 42px;")
        self.start_button.setMaximumWidth(self.start_button.sizeHint().width())
        center_container_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # Test Bench switch
        switch_layout = QVBoxLayout()
        self.test_bench_label = QLabel("Test Bench")
        self.test_bench_label.setStyleSheet("font-size: 32px;")
        self.test_bench_switch = QCheckBox()
        self.test_bench_switch.setStyleSheet("""
            QCheckBox::indicator { width: 60px; height: 40px; background-color: grey; }
            QCheckBox::indicator:checked { background-color: green; }
        """)
        self.test_bench_switch.setChecked(False)
        self.test_bench_switch.stateChanged.connect(self.toggle_test_bench)
        switch_layout.addWidget(self.test_bench_label, alignment=Qt.AlignCenter)
        switch_layout.addWidget(self.test_bench_switch, alignment=Qt.AlignCenter)
        center_container_layout.addLayout(switch_layout)

        main_layout.addWidget(center_container, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        self.showMaximized()

    def toggle_test_bench(self, state):
        if state == Qt.Checked:
            self.test_bench_switch.setStyleSheet("""
                QCheckBox::indicator { width: 60px; height: 40px; background-color: green; }
            """)
        else:
            self.test_bench_switch.setStyleSheet("""
                QCheckBox::indicator { width: 60px; height: 40px; background-color: grey; }
            """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrainEngineer()
    window.show()
    sys.exit(app.exec_())
