import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QFormLayout, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView
from train_system.common.time_keeper import TimeKeeper
from train_system.train_model.train_model import TrainModel

class TrainModelUI(QWidget):
    def __init__(self, train_model, time_keeper):
        super().__init__()
        self.time_keeper = time_keeper
        self.time_keeper.start_timer()
        self.train_model = train_model
        self.time_keeper.tick.connect(self.refresh_tables)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create tab widget
        tab_widget = QTabWidget()
        tabs = ["MBO", "CTC Office", "Track Model", "Train Model", "SW Track Controller", 
                "HW Track Controller", "SW Train Controller", "HW Train Controller"]
        for tab_name in tabs:
            tab_widget.addTab(QWidget(), tab_name)

        # Set default tab
        tab_widget.setCurrentIndex(tabs.index("Train Model"))
        main_layout.addWidget(tab_widget)

        # Create content area layout
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Create tables
        self.tables = {}
        table_layout = QVBoxLayout()

        for title in ["Emergency / Failure Status", "Train Information: Vital", "Train Information: Non-Vital"]:
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["", "Value"])

            # Set header resize mode
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setVisible(False)  # Hide header row

            self.tables[title] = table
            self.populate_table(table, title)
            table_layout.addWidget(table)

        # Create failure buttons and emergency brake button
        self.failure_buttons = {
            "Engine Failure": self.train_model.toggle_engine_failure,
            "Brake Failure": self.train_model.toggle_brake_failure,
            "Signal Failure": self.train_model.toggle_signal_failure,
            "Emergency Brake": self.train_model.toggle_emergency_brake
        }

        self.failure_buttons_widgets = {}
        for label, toggle_func in self.failure_buttons.items():
            button = QPushButton(label)
            button.setCheckable(True)
            button.setChecked(getattr(self.train_model, f"get_{label.replace(' ', '_').lower()}")())
            button.clicked.connect(lambda _, func=toggle_func: func())
            self.failure_buttons_widgets[label] = button
            table_layout.addWidget(button)

        # Create input form
        input_form = QFormLayout()
        self.cmd_speed_input = QLineEdit()
        self.cmd_speed_input.setPlaceholderText("Commanded Speed (m/s)")
        input_form.addRow("Commanded Speed:", self.cmd_speed_input)

        self.authority_input = QLineEdit()
        self.authority_input.setPlaceholderText("Authority (meters)")
        input_form.addRow("Authority:", self.authority_input)

        # Add Commanded Power input
        self.cmd_power_input = QLineEdit()
        self.cmd_power_input.setPlaceholderText("Commanded Power (units)")
        input_form.addRow("Commanded Power:", self.cmd_power_input)

        # Toggle Buttons
        self.toggle_buttons = {
            "Service Brake": self.train_model.toggle_service_brake,
            "Right Side Doors": self.train_model.toggle_right_side_doors,
            "Left Side Doors": self.train_model.toggle_left_side_doors,
            "Exterior Lights": self.train_model.toggle_exterior_lights,
            "Interior Lights": self.train_model.toggle_interior_lights,
            "AC": self.train_model.toggle_ac,
            "Heater": self.train_model.toggle_heater
        }

        self.toggle_buttons_widgets = {}
        for label, toggle_func in self.toggle_buttons.items():
            button = QPushButton(label)
            button.setCheckable(True)
            button.setChecked(getattr(self.train_model, f"get_{label.replace(' ', '_').lower()}")())
            button.clicked.connect(lambda _, func=toggle_func: func())
            self.toggle_buttons_widgets[label] = button
            input_form.addRow(label, button)

        # Update Button
        btn_update_values = QPushButton("Update Values")
        btn_update_values.clicked.connect(self.update_values)
        input_form.addRow(btn_update_values)

        input_area = QWidget()
        input_area.setLayout(input_form)

        # Add tables and input area to content layout
        content_layout.addLayout(table_layout, stretch=2)
        content_layout.addWidget(input_area)

        # Set the window title and show the UI
        self.setWindowTitle('Train Model')
        self.show()

    def populate_table(self, table, title):
        data_fetchers = {
            "Emergency / Failure Status": [
                ("Engine Failure", lambda: str(self.train_model.get_engine_failure())),
                ("Brake Failure", lambda: str(self.train_model.get_brake_failure())),
                ("Signal Failure", lambda: str(self.train_model.get_signal_failure())),
                ("Emergency Brake", lambda: "Engaged" if self.train_model.get_emergency_brake() else "Disengaged")
            ],
            "Train Information: Vital": [
                ("Current Speed", lambda: str(self.train_model.get_current_speed()) + " m/s"),
                ("Commanded Speed", lambda: str(self.train_model.commanded_speed) + " m/s"),
                ("Authority", lambda: str(self.train_model.authority) + " meters"),
                ("Service Brake Status", lambda: "Engaged" if self.train_model.get_service_brake() else "Disengaged"),
                ("Commanded Power", lambda: str(self.train_model.commanded_power) + " kW")
            ],
            "Train Information: Non-Vital": [
                ("On-Board Passengers", lambda: str(self.train_model.get_passengers())),
                ("Right Side Door Status", lambda: str(self.train_model.get_right_side_doors())),
                ("Left Side Door Status", lambda: str(self.train_model.get_left_side_doors())),
                ("Exterior Lights", lambda: str(self.train_model.get_exterior_lights())),
                ("Interior Lights", lambda: str(self.train_model.get_interior_lights())),
                ("AC Status", lambda: str(self.train_model.get_ac())),
                ("Heater Status", lambda: str(self.train_model.get_heater())),
                ("Internal Temperature", lambda: str(self.train_model.get_train_temp()))
            ]
        }
        table.setRowCount(len(data_fetchers[title]))
        for row, (label, fetcher) in enumerate(data_fetchers[title]):
            table.setItem(row, 0, QTableWidgetItem(label))
            table.setItem(row, 1, QTableWidgetItem(fetcher()))

    def update_values(self):
        # Update commanded speed, authority, and commanded power
        cmd_speed = self.cmd_speed_input.text()
        authority = self.authority_input.text()
        cmd_power = self.cmd_power_input.text()

        if cmd_speed:
            self.train_model.set_commanded_speed(float(cmd_speed))
        if authority:
            self.train_model.set_authority(float(authority))
        if cmd_power:
            self.train_model.set_power(float(cmd_power))

        # Refresh tables
        self.refresh_tables()

    def refresh_tables(self):
        for title in self.tables.keys():
            self.populate_table(self.tables[title], title)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    time_keeper = TimeKeeper() 
    time_keeper.start_timer()
    train_model = TrainModel(train_id=1, time_keeper=time_keeper)
    ui = TrainModelUI(train_model, time_keeper)
    ui.show()
    sys.exit(app.exec())
