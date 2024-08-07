from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QComboBox, 
                             QAbstractItemView)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, pyqtSlot
from typing import Optional

from train_system.common.palette import Colors
from train_system.common.line import Line
from train_system.common.track_switch import TrackSwitch

class TrackSwitchWidget(QWidget):
    def __init__(self, line: Line, parent: Optional[QWidget] = None) -> None:

        """
        Initializes the TrackSwitchWidget.

        Args:
            line (Line): The line object containing track blocks.
            parent (Optional[QWidget]): The parent widget.
        """

        super().__init__(parent)
        self.title = "Track Switches"
        self.line = line
        self.rows = len(line.track_blocks)
        self.cols = 2
        self.headers = ["Switch ID", "Status"]
        self.init_ui()

    def init_ui(self) -> None:

        """
        Initializes the user interface.
        """

        layout = QVBoxLayout()

        # Create table title
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            f"background-color: {Colors.BLACK};"
            f"color: {Colors.WHITE};"
            "font-size: 16pt;"
            "font-weight: 600;"
        )
        layout.addWidget(title_label)

        # Create table widget
        self.table = QTableWidget(self.rows, self.cols)
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.verticalHeader().setVisible(False)

        # Set the style for the table headers and cells
        self.table.setStyleSheet(f"""
            QHeaderView::section {{ 
                background-color: {Colors.GREY};
                color: {Colors.BLACK};
                font-size: 14pt;
            }}
            QTableWidget::item {{
                background-color: {Colors.WHITE};
                color: {Colors.BLACK};
                border: 1px solid {Colors.BLACK}; 
            }}
            QTableWidget {{
                background-color: {Colors.GREY};
                gridline-color: {Colors.BLACK};
            }}
        """)

        # Set the palette for the table to control the background and text colors
        palette = self.table.palette()
        self.table.setPalette(palette)

        # Adjust column widths to fit contents
        self.table.horizontalHeader().setStretchLastSection(True)
        for col in range(self.cols):
            self.table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.Stretch
            )

        # Add data to the table
        self.update_table_data()

        # Connect the line switch signal to the update switch position slot
        self.line.switch_position_updated.connect(self.update_switch_position)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_table_data(self) -> None:

        """
        Updates the table data with the current track block statuses.
        """

        self.rows = len(self.line.switches)
        self.table.setRowCount(self.rows)
        for i, switch in enumerate(self.line.switches):
            switch_cell = QTableWidgetItem(str(switch.number))
            switch_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            switch_cell.setFlags(
                switch_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(i, 0, switch_cell)

            # ComboBox for switch status
            status_cell = QComboBox()
            option_1 = f"{switch.parent_block} -> {switch.child_blocks[0]}"
            option_2 = f"{switch.parent_block} -> {switch.child_blocks[1]}"
            status_cell.addItems([option_1, option_2])
            status_cell.setCurrentText(
                option_1 if switch.position == switch.child_blocks[0] else option_2
            )
            status_cell.currentTextChanged.connect(
                lambda state, sw=switch: sw.toggle()
            )
            status_cell.setStyleSheet(
                f"background-color: {Colors.WHITE}; color: {Colors.BLACK};"
            )
            self.table.setCellWidget(i, 1, status_cell)

    def update_switch_position(self, switch: TrackSwitch, state: str) -> None:

        """
        Updates the switch position of a track switch.

        Args:
            track_switch (TrackSwitch): The track block to update.
            state (str): The new position.
        """

        self.update_table_data()

    def set_line(self, line: Line) -> None:

        """
        Sets the line object for the widget.

        Args:
            line (Line): The line object.
        """

        self.line = line
        self.rows = len(line.switches)
        self.update_table_data()

    @pyqtSlot(str, int, int)
    def update_switch_position(self, line_name: str, switch_number: int, new_position: int) -> None:

        """
        Updates the switch position of a track switch.
        Used to updated options when switches are changed by track controller.

        Args:
            line_name (str): The name of the line.
            switch_number (int): The number of the switch.
            new_position (int): The new position.
        """

        self.update_table_data()
