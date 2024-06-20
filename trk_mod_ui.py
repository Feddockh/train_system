from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from gui_features import CustomTable
from testbench_datatypes import TestbenchDatatype
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Track Model")

        self.views = QStackedWidget()
        self.builder_view = BuilderView()
        self.builder_view.setParent(self.views)
        self.murphy_view = MurphyView()
        self.murphy_view.setParent(self.views)
        self.views.addWidget(self.builder_view)
        self.views.addWidget(self.murphy_view)

        self.views.setCurrentIndex(0)
        self.setFixedSize(1222, 702)
        self.setCentralWidget(self.views)

        self.test_window = TestWindow()

    def draw_tables(self, occupied_list, sales_2d_list, signals_2d_list, switches_2d_list):
        self.murphy_view.update_tables(occupied_list, sales_2d_list, signals_2d_list, switches_2d_list)

    def get_view(self):
        return self.views.currentIndex()
    
    def test_input(self):
        print("in main window of ui")
        return self.test_window.retrieve_current_input()


class BuilderView(QWidget):
    def __init__(self):
        super().__init__()

        self.builder_buttons = QVBoxLayout()
        self.track_layout_button = QPushButton("Upload Track Layout")
        self.track_layout_button.setFixedSize(280, 70)
        self.track_layout_button.clicked.connect(self.change_layout_file)
        self.murphy_view_button = QPushButton("Murphy View")
        self.murphy_view_button.setFixedSize(160, 45)
        self.murphy_view_button.clicked.connect(self.switch_to_murphy_view)

        self.builder_buttons.addWidget(self.track_layout_button, 0, Qt.AlignmentFlag.AlignHCenter)
        self.builder_buttons.addWidget(self.murphy_view_button, 0, Qt.AlignmentFlag.AlignHCenter)

        self.map_img = QLabel()
        self.map_img_pixmap = QPixmap('map.png')
        self.map_img.setPixmap(self.map_img_pixmap)
        self.map_img.setScaledContents(True)

        self.whole_layout = QHBoxLayout()
        self.whole_layout.addWidget(self.map_img)
        self.whole_layout.addLayout(self.builder_buttons)

        self.setLayout(self.whole_layout)


    def change_layout_file(self):
        print("layout button")

    def switch_to_murphy_view(self):
        self.parentWidget().setCurrentIndex(1)


class MurphyView(QWidget):
    def __init__(self):
        super().__init__()

        num_blocks = 12
        occupied_blocks = []
        num_stations = 2
        ticket_sales = [["a", ""], ["b", ""], ["c", ""]]
        num_signals = 5
        signal_states = [["AB", "Green"], ["CD", "Green"], ["EF", "Red"], ["GH", "Red"], ["IJ", "Green"]]
        num_switches = 5
        switch_states = [["AB", "A"], ["CD", "C"], ["EF", "E"], ["GH", "G"], ["IJ", "I"]]

        self.failure_menu = QVBoxLayout()
        self.failure_menu_title = QLabel("Create Failure")
        self.failure_block_select = QComboBox()
        self.failure_block_select.addItems(["1","2","3"])
        self.failure_circuit = QPushButton("Circuit")
        self.failure_circuit.clicked.connect(self.circuit_fail)
        self.failure_power = QPushButton("Power")
        self.failure_power.clicked.connect(self.power_fail)
        self.failure_rail = QPushButton("Break Rail")
        self.failure_rail.clicked.connect(self.rail_fail)

        self.failure_menu.addWidget(self.failure_menu_title)
        self.failure_menu.addWidget(self.failure_block_select)
        self.failure_menu.addWidget(self.failure_circuit)
        self.failure_menu.addWidget(self.failure_power)
        self.failure_menu.addWidget(self.failure_rail)

        self.tables = QGridLayout()
        self.occupied_blocks_table = CustomTable("Occupied Blocks", num_blocks, 2, ["Blue", ""], occupied_blocks)
        self.ticket_sales_table = CustomTable("Ticket Sales", 300, 2, ["Station", "Sales"], ticket_sales)
        self.signal_states_table = CustomTable("Signal States", num_signals, 2, ["Location", "State"], signal_states)
        self.switch_states_table = CustomTable("Switch States", num_switches, 2, ["Switch", "State"], switch_states)

        self.tables.addWidget(self.occupied_blocks_table, 0, 0)
        self.tables.addWidget(self.ticket_sales_table, 0, 1)
        self.tables.addWidget(self.signal_states_table, 1, 0)
        self.tables.addWidget(self.switch_states_table, 1, 1)

        self.test_and_heat = QHBoxLayout()
        self.test_button = QPushButton("Test")
        self.test_button.clicked.connect(self.test_clicked)
        self.heater_state = QLabel("Track Heaters OFF")
        self.temp = QLabel("84F Outside")

        self.test_and_heat.addWidget(self.test_button)
        self.test_and_heat.addWidget(self.heater_state)
        self.test_and_heat.addWidget(self.temp)

        self.left_side = QVBoxLayout()
        self.left_side.addLayout(self.failure_menu)
        self.left_side.addLayout(self.tables)
        self.left_side.addLayout(self.test_and_heat)
        

        self.layout_controls = QHBoxLayout()
        self.line_toggle = QPushButton("Show Blue Line")
        self.line_toggle.setCheckable(True)
        self.line_toggle.clicked.connect(self.line_toggle_click)
        self.builder_view = QPushButton("Track Builder View")
        self.builder_view.clicked.connect(self.builder_view_click)
        self.layout_view = QPushButton("Layout View")
        self.layout_view.clicked.connect(self.layout_view_click)

        self.layout_controls.addWidget(self.line_toggle)
        self.layout_controls.addWidget(self.builder_view)
        self.layout_controls.addWidget(self.layout_view)

        self.map_img = QLabel()
        self.map_img_pixmap = QPixmap('map.png')
        self.map_img.setPixmap(self.map_img_pixmap)
        self.map_img.setScaledContents(True)

        self.right_side = QVBoxLayout()
        self.right_side.addLayout(self.layout_controls)
        self.right_side.addWidget(self.map_img)

        self.whole_layout = QHBoxLayout()
        self.whole_layout.addLayout(self.left_side)
        self.whole_layout.addLayout(self.right_side)

        self.setLayout(self.whole_layout)


    def circuit_fail(self):
        print("circuit ", str(self.failure_block_select.currentIndex()+1))

    def power_fail(self):
        print("power ", str(self.failure_block_select.currentIndex()+1))

    def rail_fail(self):
        print("rail ", str(self.failure_block_select.currentIndex()+1))

    def test_clicked(self):
        self.t = TestWindow()
        self.t.show()

    def line_toggle_click(self):
        if self.line_toggle.isChecked():
            print("showing line")
        else:
            print("hiding line")

    def builder_view_click(self):
        self.parentWidget().setCurrentIndex(0)

    def layout_view_click(self):
        print("layout view")

    def update_tables(self, occupied_list, sales_2d_list, signals_2d_list, switches_2d_list):
        self.occupied_blocks_table.update_table_data(occupied_list)
        self.ticket_sales_table.update_table_data(sales_2d_list)
        self.signal_states_table.update_table_data(signals_2d_list)
        self.switch_states_table.update_table_data(switches_2d_list)


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.current_input = []

        self.layout = QGridLayout()
        
        self.layout.addWidget(QLabel("Add Occupancy"), 0, 0)
        self.add_occ = QLineEdit()
        self.add_occ_confirm = QPushButton()
        self.add_occ_confirm.clicked.connect(self.add_occ_input)
        self.layout.addWidget(self.add_occ, 0, 1)
        self.layout.addWidget(self.add_occ_confirm, 0, 2)

        self.layout.addWidget(QLabel("Remove Occupancy"), 1, 0)
        self.rem_occ = QLineEdit()
        self.rem_occ_confirm = QPushButton()
        self.rem_occ_confirm.clicked.connect(self.rem_occ_input)
        self.layout.addWidget(self.rem_occ, 1, 1)
        self.layout.addWidget(self.rem_occ_confirm, 1, 2)

        self.setLayout(self.layout)

    def add_occ_input(self):
        self.current_input = [TestbenchDatatype.ADD_OCC, self.add_occ.text()]

    def rem_occ_input(self):
        self.current_input = [TestbenchDatatype.REM_OCC, self.rem_occ.text()]

    def retrieve_current_input(self):
        to_return = self.current_input
        self.current_input.clear()
        return to_return


app = QApplication([])

window = MainWindow()
window.show()

app.exec()