import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QFormLayout, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView
from train_system.common.time_keeper import TimeKeeper
from train_system.train_model.train_model_v4 import TrainModel

class TrainModelUI(QWidget) :

    # this function initialized the ui display a TrainModel instance
    # paramters : TrainModel train_model, TimeKeeper time_keeper
    def __init__(self, train_model, time_keeper):

        super().__init__()
        self.train_model = train_model
        self.time_keeper = time_keeper
        self.time_keeper.tick.connect(self.refresh_tables)
        self.initUI()

    # this function initialized and display the UI for the train model
    def initUI(self):

        # establish main UI layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # create content area layout
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # create tables
        self.tables = {}
        table_layout = QVBoxLayout()
        
        # table properties
        for title in ["Emergency / Fault Status", "Train Information: Vital", "Train Information: Non-Vital"]:
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

        # Create fault buttons and emergency brake button
        self.fault_buttons = {
            "Engine Fault": self.train_model.toggle_engine_fault,
            "Brake Fault": self.train_model.toggle_brake_fault,
            "Signal Fault": self.train_model.toggle_signal_fault,
            "Emergency Brake": self.train_model.toggle_emergency_brake
        }

        self.fault_buttons_widgets = {}
        for label, toggle_func in self.fault_buttons.items():
            button = QPushButton(label)
            button.setCheckable(True)
            button.setChecked(getattr(self.train_model, f"get_{label.replace(' ', '_').lower()}")())
            button.clicked.connect(lambda _, func=toggle_func: func())
            self.fault_buttons_widgets[label] = button
            table_layout.addWidget(button)

        # Create input form
        input_form = QFormLayout()
        self.cmd_speed_input = QLineEdit()
        self.cmd_speed_input.setPlaceholderText("(miles per hour)")
        input_form.addRow("Commanded Speed:", self.cmd_speed_input)

        self.authority_input = QLineEdit()
        self.authority_input.setPlaceholderText("(feet)")
        input_form.addRow("Authority:", self.authority_input)

        # Add Commanded Power input
        self.cmd_power_input = QLineEdit()
        self.cmd_power_input.setPlaceholderText("(kW)")
        input_form.addRow("Commanded Power:", self.cmd_power_input)

        self.grade_input = QLineEdit()
        self.grade_input.setPlaceholderText("(degrees)")
        input_form.addRow("Grade:", self.grade_input)

        self.passengers_input = QLineEdit()
        self.passengers_input.setPlaceholderText("(people)")
        input_form.addRow("Passengers:", self.passengers_input)

        # Toggle Buttons
        self.toggle_buttons = {
            "Service Brake": self.train_model.toggle_service_brake,
            "Right Doors": self.train_model.toggle_right_doors,
            "Left Doors": self.train_model.toggle_left_doors,
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
            "Emergency / Fault Status": [
                ("Engine Fault", lambda: "FAULT!" if self.train_model.get_engine_fault() else "No Fault"),
                ("Brake Fault", lambda: "FAULT!" if self.train_model.get_brake_fault() else "No Fault"),
                ("Signal Fault", lambda: "FAULT!" if self.train_model.get_signal_fault() else "No Fault"),
                ("Emergency Brake", lambda: "Engaged" if self.train_model.get_emergency_brake() else "Disengaged")
            ],
            "Train Information: Vital": [
                ("Current Speed", lambda: str(round(self.train_model.get_current_speed() * 2.23694, 2)) + " miles per hour"),
                ("Current Acceleration", lambda: str(round(self.train_model.get_current_acceleration() * 3.28084, 2)) + " ft/s/s"),
                ("Commanded Speed", lambda: str(round(self.train_model.get_commanded_speed() * 2.23694, 2)) + " miles per hour"),
                ("Authority", lambda: str(round(self.train_model.get_authority().get_distance() * 3.28084, 2)) + " feet"),
                ("Service Brake Status", lambda: "Engaged" if self.train_model.get_service_brake() else "Disengaged"),
                ("Commanded Power", lambda: str(round(self.train_model.get_power_command(), 2)) + " kW"),
                ("Length", lambda: str(round(self.train_model.TRAIN_LENGTH * 3.28084, 2)) + " feet"),
                ("Empty Train Mass", lambda: str(round(self.train_model.EMPTY_TRAIN_MASS / 907.185, 2)) + " tons"),
                ("Train Mass with Passengers", lambda: str(round((self.train_model.EMPTY_TRAIN_MASS + (self.train_model.passengers * self.train_model.PASSENGER_MASS)) / 907.185, 2)) + " tons"),
                ("Encrypted MBO Data", lambda: self.train_model.encrypted_speed + self.train_model.encrypted_authority)
            ],
            "Train Information: Non-Vital": [
                ("On-Board Crew", lambda: str(self.train_model.get_crew())),
                ("On-Board Passengers", lambda: str(self.train_model.get_passengers() - 2)),
                ("Right Door Status", lambda: "Open" if self.train_model.get_right_doors() else "Closed"),
                ("Left Door Status", lambda: "Open" if self.train_model.get_left_doors() else "Closed"),
                ("Exterior Lights", lambda: "On" if self.train_model.get_exterior_lights() else "Off"),
                ("Interior Lights", lambda: "On" if self.train_model.get_interior_lights() else "Off"),
                ("AC Status", lambda: "On" if self.train_model.get_ac() else "Off"),
                ("Heater Status", lambda: "On" if self.train_model.get_heater() else "Off"),
                ("Internal Temperature", lambda: str(round(self.train_model.get_current_temp(), 1)) + " degrees Fahrenheit"),
                ("Train Width", lambda: str(round(self.train_model.TRAIN_WIDTH * 3.28084, 2)) + " feet"),
                ("Train Height", lambda: str(round(self.train_model.TRAIN_HEIGHT * 3.28084, 2)) + " feet"),
                ("Advertisement", lambda: self.train_model.get_advertisement())
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
        grade = self.grade_input.text()
        passengers = self.passengers_input.text()

        if cmd_speed:
            self.train_model.set_commanded_speed(float(cmd_speed))
        if authority:
            self.train_model.set_authority(float(authority) / 3.28084)
        if cmd_power:
            self.train_model.set_power_command(float(cmd_power))
        if grade :
            self.train_model.set_current_grade(float(grade))
        if passengers :
            self.train_model.set_passengers(float(passengers))

        # Refresh tables
        self.refresh_tables()

    def refresh_tables(self):
        for title in self.tables.keys():
            self.populate_table(self.tables[title], title)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    time_keeper = TimeKeeper() 
    time_keeper.start_timer()
    train_model = TrainModel(time_keeper, 1, "green")
    ui = TrainModelUI(train_model, time_keeper)
    ui.show()
    sys.exit(app.exec())
