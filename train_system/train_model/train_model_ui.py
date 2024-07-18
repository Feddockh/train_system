import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QPushButton

from train_system.common.time_keeper import TimeKeeper
from train_system.train_model.train_model import TrainModel

class TrainModelUI(QWidget) :
    def __init__(self, train_model) :
        super().__init__()
        self.train_model = train_model

        self.initUI()

    def initUI(self) :
        # Create main layout
        layout = QVBoxLayout()

        # Create tab widget
        tab_widget = QTabWidget()

        # Add tabs
        tabs = ["MBO", "CTC Office", "Track Model", "Train Model", "SW Track Controller", 
                "HW Track Controller", "SW Train Controller", "HW Train Controller"]
        for tab_name in tabs :
            tab_widget.addTab(QWidget(), tab_name)

        # Set default tab
        tab_widget.setCurrentIndex(tabs.index("Train Model"))

        # Add tab widget to layout
        layout.addWidget(tab_widget)

        # Create tables
        tables = []
        for title in ["Emergency / Failure Status", "Train Information: Vital", "Train Information: Non-Vital"]:
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Data Label", "Value"])
            table.setRowCount(len(self.train_model.get_failures()))  # Adjust row count based on data

            # Populate table with data from TrainModel instance
            self.populate_table(table, title)
            tables.append(table)

        # Add tables to layout
        for table in tables:
            layout.addWidget(table)

        # Create buttons
        btn_toggle_engine_failure = QPushButton("Toggle Engine Failure")
        btn_toggle_brake_failure = QPushButton("Toggle Brake Failure")
        btn_toggle_signal_failure = QPushButton("Toggle Signal Failure")
        btn_toggle_emergency_brake = QPushButton("Toggle Emergency Brake")

        # Connect buttons to TrainModel methods
        btn_toggle_engine_failure.clicked.connect(self.train_model.toggle_engine_failure)
        btn_toggle_brake_failure.clicked.connect(self.train_model.toggle_brake_failure)
        btn_toggle_signal_failure.clicked.connect(self.train_model.toggle_signal_failure)
        btn_toggle_emergency_brake.clicked.connect(self.train_model.toggle_emergency_brake)

        # Add buttons to layout
        layout.addWidget(btn_toggle_engine_failure)
        layout.addWidget(btn_toggle_brake_failure)
        layout.addWidget(btn_toggle_signal_failure)
        layout.addWidget(btn_toggle_emergency_brake)

        # Set the layout to the main window
        self.setLayout(layout)
        self.setWindowTitle('Train Model UI')
        self.show()

    def populate_table(self, table, title) :
        if title == "Emergency / Failure Status" :
            data = [
                ("Engine Failure", str(self.train_model.get_engine_failure())),
                ("Brake Failure", str(self.train_model.get_brake_failure())),
                ("Signal Failure", str(self.train_model.get_signal_failure())),
                ("Emergency Brake", "Engaged" if self.train_model.get_emergency_brake() else "Disengaged")
            ]
        elif title == "Train Information: Vital" :
            data = [
                ("Current Speed", str(self.train_model.get_current_speed()) + " m/s"),
                ("Commanded Speed", str("commanded speed") + " m/s"),
                ("Authority", str("authority") + " meters"),
                ("Service Brake Status", "Engaged" if self.train_model.get_service_brake() else "Disengaged")
            ]
        elif title == "Train Information: Non-Vital" :
            data = [
                ("On-Board Passengers", str(self.train_model.get_passengers())),
                ("Right Side Door Status", str(self.train_model.get_right_side_doors())),
                ("Left Side Door Status", str(self.train_model.get_left_side_doors())),
                ("Exterior Lights", str(self.train_model.get_exterior_lights())),
                ("Interior Lights", str(self.train_model.get_intetior_lights())),
                ("AC Status", str(self.train_model.get_ac())),
                ("Heater Status", str(self.train_model.get_heater())),
                ("Internal Temperature", str(self.train_model.get_train_temp()))
            ]

        # Populate table with data
        for row, (label, value) in enumerate(data) :
            table.setItem(row, 0, QTableWidgetItem(label))
            table.setItem(row, 1, QTableWidgetItem(value))

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create an instance of TrainModel (you need to instantiate with appropriate parameters)
    time_keeper = TimeKeeper()
    time_keeper.start_timer()
    train_model = TrainModel(1, time_keeper)  # Adjust parameters as needed

    # Create the UI instance and run the application
    ex = TrainModelUI(train_model)
    sys.exit(app.exec())
