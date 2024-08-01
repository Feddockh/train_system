import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QFormLayout, QLineEdit, QLabel
from PyQt6.QtWidgets import QHeaderView
from train_system.common.palette import Colors
from train_system.common.time_keeper import TimeKeeper
from train_system.train_model.train_model_v4 import TrainModel

# this class creates the UI i/o for the Train Model module
class TrainModelUI(QWidget) :

    # this function initialized the ui display a TrainModel instance
    # paramters : TrainModel train_model, TimeKeeper time_keeper
    def __init__(self, train_model, time_keeper) :

        super().__init__()
        self.train_model = train_model
        self.time_keeper = time_keeper
        self.time_keeper.tick.connect(self.refresh_tables)
        self.initUI()

    # this function initialized and display the UI for the train model
    def initUI(self) :

        # establish main UI layout
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        self.setStyleSheet(f"background-color: {Colors.WHITE};")
        left_layout = QVBoxLayout()
        center_layout = QVBoxLayout()
        
        # create tables
        self.tables = {}
        
        # define the tables
        for title in ["Emergency / Fault Status", "Train Information: Vital"] :

            # set table layout and headers
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["", "Value"])
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setVisible(False)  
            self.tables[title] = table
            self.populate_table(table, title)
            left_layout.addWidget(table)

        # create the "Train Information: Non-Vital" table
        self.non_vital_table = QTableWidget()
        self.non_vital_table.setColumnCount(2)
        self.non_vital_table.setHorizontalHeaderLabels(["", "Value"])
        self.populate_table(self.non_vital_table, "Train Information: Non-Vital")
        self.non_vital_table.setMinimumSize(400, 390)
        
        # create fault buttons and emergency brake button
        fault_buttons_layout = QVBoxLayout()
        self.fault_buttons = {
            "Engine Fault": self.train_model.toggle_engine_fault,
            "Brake Fault": self.train_model.toggle_brake_fault,
            "Signal Fault": self.train_model.toggle_signal_fault,
            "Emergency Brake": self.train_model.toggle_emergency_brake}

        # create fault widget and add buttons
        self.fault_buttons_widgets = {}
        for label, toggle_func in self.fault_buttons.items() :
            button = QPushButton(label)
            button.setCheckable(True)
            button.setChecked(getattr(self.train_model, f"get_{label.replace(' ', '_').lower()}")())
            button.clicked.connect(lambda _, func=toggle_func: func())
            if label == "Emergency Brake" :
                button.setStyleSheet(f"background-color: {Colors.RED};")
            else :
                button.setStyleSheet(f"background-color: {Colors.YELLOW}; color: {Colors.BLACK}")
            self.fault_buttons_widgets[label] = button
            fault_buttons_layout.addWidget(button)
        fault_buttons_widget = QWidget()
        fault_buttons_widget.setLayout(fault_buttons_layout)

        # create test bench
        input_form = QFormLayout()
        label = QLabel("Test Bench:")
        label.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {Colors.BLACK};")
        input_form.addRow(label, None)

        # commanded speed testbech input
        self.cmd_speed_input = QLineEdit()
        self.cmd_speed_input.setStyleSheet(f"background-color: {Colors.GREY}; color: {Colors.BLACK};")
        self.cmd_speed_input.setPlaceholderText("(miles per hour)")
        label = QLabel("Enter Commanded Speed:")
        label.setStyleSheet(f"color: {Colors.BLACK};")
        input_form.addRow(label, self.cmd_speed_input)

        # authority testbech input
        self.authority_input = QLineEdit()
        self.authority_input.setPlaceholderText("(feet)")
        self.authority_input.setStyleSheet(f"background-color: {Colors.GREY}; color: {Colors.BLACK};")
        label = QLabel("Enter Authority:")
        label.setStyleSheet(f"color: {Colors.BLACK};")
        input_form.addRow(label, self.authority_input)

        # commanded power testbech input
        self.cmd_power_input = QLineEdit()
        self.cmd_power_input.setPlaceholderText("(kW)")
        self.cmd_power_input.setStyleSheet(f"background-color: {Colors.GREY}; color: {Colors.BLACK};")
        label = QLabel("Enter Commanded Power:")
        label.setStyleSheet(f"color: {Colors.BLACK};")
        input_form.addRow(label, self.cmd_power_input)

        # grade testbech input
        self.grade_input = QLineEdit()
        self.grade_input.setPlaceholderText("(degrees)")
        self.grade_input.setStyleSheet(f"background-color: {Colors.GREY}; color: {Colors.BLACK};")
        label = QLabel("Enter Grade:")
        label.setStyleSheet(f"color: {Colors.BLACK};")
        input_form.addRow(label, self.grade_input)

        # passengers testbech input
        self.passengers_input = QLineEdit()
        self.passengers_input.setPlaceholderText("(people)")
        self.passengers_input.setStyleSheet(f"background-color: {Colors.GREY}; color: {Colors.BLACK};")
        label = QLabel("Enter Passengers:")
        label.setStyleSheet(f"color: {Colors.BLACK};")
        input_form.addRow(label, self.passengers_input)

        # update values testbench button
        btn_update_values = QPushButton("Update Values")
        btn_update_values.clicked.connect(self.update_values)
        btn_update_values.setStyleSheet(f"background-color: {Colors.GREEN}; color: {Colors.BLACK};")
        input_form.addRow(btn_update_values)
      
        # testbench toggle buttons
        self.toggle_buttons = {
            "Service Brake": self.train_model.toggle_service_brake,
            "Right Doors": self.train_model.toggle_right_doors,
            "Left Doors": self.train_model.toggle_left_doors,
            "Exterior Lights": self.train_model.toggle_exterior_lights,
            "Interior Lights": self.train_model.toggle_interior_lights,
            "AC": self.train_model.toggle_ac,
            "Heater": self.train_model.toggle_heater
        }

        # create and add testbench toggle buttons to testbench
        self.toggle_buttons_widgets = {}
        for label, toggle_func in self.toggle_buttons.items():
            button = QPushButton(label)
            button.setCheckable(True)
            button.setChecked(getattr(self.train_model, f"get_{label.replace(' ', '_').lower()}")())
            button.clicked.connect(lambda _, func=toggle_func: func())
            button.setStyleSheet(f"background-color: {Colors.BLUE}; color: {Colors.BLACK};")
            self.toggle_buttons_widgets[label] = button
            row_label = QLabel(str("Toggle " + label))
            row_label.setStyleSheet(f"color: {Colors.BLACK};")
            input_form.addRow(row_label, button)
        input_area = QWidget()
        input_area.setLayout(input_form)

        # update main_layout
        main_layout.addLayout(left_layout, stretch=2)
        center_layout.addWidget(self.non_vital_table)
        center_layout.addWidget(fault_buttons_widget)
        main_layout.addLayout(center_layout, stretch=1)
        main_layout.addWidget(input_area)

        # set the window and show the UI
        self.setFixedSize(950, 550)
        self.setWindowTitle('Train Model')
        self.show()

    # this function will update the UI tables with the data stored in the Train Model class
    # parameters : table and title
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
                ("Authority", lambda: str(round(self.train_model.get_authority() * 3.28084, 2)) + " feet"),
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

        # update table headers and format
        if title == "Emergency / Fault Status":
            table.setFixedSize(300, 150)
        elif title == "Train Information: Vital":
            table.setFixedSize(300, 330)
        else:
            table.setMinimumSize(355, 300)
        table.setRowCount(len(data_fetchers[title]))
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(True)
        header = table.horizontalHeader()
        header.setStyleSheet("font-size: 12px; font-weight: bold;")
        table.setHorizontalHeaderLabels([title, ''])

        # update table data
        for row, (label, fetcher) in enumerate(data_fetchers[title]):
            table.setItem(row, 0, QTableWidgetItem(label))
            table.setItem(row, 1, QTableWidgetItem(fetcher()))
            table.setStyleSheet(f"background-color: {Colors.GREY}; color: {Colors.BLACK};")
        table.setColumnWidth(0, 175)
        table.setColumnWidth(1, 175)

    # this function updates values in the Train Model instance from the accepted values from the testbench
    def update_values(self):

        # read text box input
        cmd_speed = self.cmd_speed_input.text()
        authority = self.authority_input.text()
        cmd_power = self.cmd_power_input.text()
        grade = self.grade_input.text()
        passengers = self.passengers_input.text()

        # update values from text box
        if cmd_speed:
            self.train_model.set_commanded_speed(float(cmd_speed) / 2.23694)
        if authority:
            self.train_model.set_authority(float(authority) / 3.28084)
        if cmd_power:
            self.train_model.set_power_command(float(cmd_power))
        if grade:
            self.train_model.set_current_grade(float(grade))
        if passengers:
            self.train_model.set_passengers(float(passengers))

        # refresh tables
        self.refresh_tables()

    # this function will refresh the table visual with any new updated information
    def refresh_tables(self):
        for title in self.tables.keys():
            self.populate_table(self.tables[title], title)
        self.populate_table(self.non_vital_table, "Train Information: Non-Vital")

# main to run Train Model code
if __name__ == '__main__':
    app = QApplication(sys.argv)
    time_keeper = TimeKeeper()
    time_keeper.start_timer()
    train_model = TrainModel(time_keeper, 1, "green")
    ui = TrainModelUI(train_model, time_keeper)
    ui.show()
    sys.exit(app.exec())
