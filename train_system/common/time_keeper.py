# train_system/common/time_keeper.py

import sys
import time
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, pyqtSlot, Qt
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QSlider, QHBoxLayout


class TimeKeeper(QThread):

    # Signal emitted every simulated second and passes the current second
    tick = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = False
        self.paused = False
        self.current_second = 0
        self.simulation_speed = 1.0
        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()

    def run(self):
        while self.running:
            self.mutex.lock()
            if self.paused:
                self.pause_condition.wait(self.mutex)
            self.mutex.unlock()
            
            time.sleep(1.0 / self.simulation_speed)
            self.current_second += 1
            self.tick.emit(self.current_second)

    def start_timer(self):
        self.running = True
        self.paused = False
        self.start()

    def pause_timer(self):
        self.mutex.lock()
        self.paused = True
        self.mutex.unlock()

    def resume_timer(self):
        self.mutex.lock()
        self.paused = False
        self.pause_condition.wakeAll()
        self.mutex.unlock()

    def set_simulation_speed(self, speed: float):
        self.simulation_speed = speed

    def stop_timer(self):
        self.running = False
        self.quit()
        self.wait()

class TimeKeeperWidget(QWidget):
    def __init__(self, time_keeper: TimeKeeper):
        super().__init__()
        self.init_ui()
        self.time_keeper = time_keeper
        time_keeper.tick.connect(self.update_label)

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.label = QLabel("00:00:00")
        self.label.setStyleSheet("font-size: 24px")
        self.layout.addWidget(self.label)

        # Create a horizontal layout for the slider and its label
        self.slider_layout = QHBoxLayout()

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(20)
        self.slider.setValue(1)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.adjust_speed)

        self.slider_label = QLabel("1.0x")
        
        self.slider_layout.addWidget(self.slider)
        self.slider_layout.addWidget(self.slider_label)

        self.layout.addLayout(self.slider_layout)
        self.setLayout(self.layout)

    @pyqtSlot(int)
    def update_label(self, current_second):
        
        # Compute the current time in hours, minutes, and seconds
        hours = current_second // 3600
        minutes = (current_second % 3600) // 60
        seconds = current_second % 60

        # Add zero padding to the minutes and seconds
        hours_str = str(hours).zfill(2)
        minutes_str = str(minutes).zfill(2)
        seconds_str = str(seconds).zfill(2)

        self.label.setText(f"{hours_str}:{minutes_str}:{seconds_str}")

    @pyqtSlot(int)
    def adjust_speed(self, speed: int):
        if speed == 0:
            self.time_keeper.pause_timer()
            self.slider_label.setText("Paused")
        else:
            self.time_keeper.resume_timer()
            self.time_keeper.set_simulation_speed(speed)
            self.slider_label.setText(f"{speed:.1f}x")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    time_keeper = TimeKeeper()
    time_keeper_widget = TimeKeeperWidget(time_keeper)
    time_keeper.start_timer()
    time_keeper_widget.show()
    sys.exit(app.exec())