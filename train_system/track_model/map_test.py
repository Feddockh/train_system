import os
import sys
import copy
import networkx as nx
from matplotlib.figure import Figure
import matplotlib.pyplot as mpl
import matplotlib

from train_system.common.track_failures import TrackFailure
matplotlib.use('QtAgg')

from PyQt6.QtWidgets import QWidget, QLayout, QApplication, QVBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from train_system.track_model.track_model import TrackModel
from train_system.common.line import Line

class Window(QWidget):

    def __init__(self, line: Line):
        super().__init__()

        self.line = line
        self.graph = nx.DiGraph()
        self.fig = mpl.figure()
        self.canvas = FigureCanvasQTAgg(self.fig)

        lo = QVBoxLayout()
        lo.addWidget(self.canvas)
        self.setLayout(lo)

        self.nodes = []
        self.edges = []

        for block in self.line.track_blocks:
            self.nodes.append(block.number)
            for num in block.connecting_blocks:
                #Do not create edges between two blocks on the "out" side of a switch
                if not (len(block.connecting_blocks) > 2 and len(block.switch_options) < 2 and len(self.line.get_track_block(num).switch_options) < 2):
                    self.edges.append([str(block.number), str(num)])

        
        self.graph.add_edges_from(self.edges)
        self.map = nx.kamada_kawai_layout(self.graph)

        self.plot()
        

    def plot(self):

        self.fig.clear()

        color_map = []
        for block in self.line.track_blocks:
            if block.track_failure != TrackFailure.NONE:
                color_map.append('orange')
            elif block.under_maintenance:
                color_map.append('yellow')
            elif block.occupancy:
                color_map.append('red')
            else:
                color_map.append('black')

        nx.draw_networkx_nodes(self.graph, self.map, node_size=1, node_color=color_map)
        nx.draw_networkx_edges(self.graph, self.map, self.graph.edges(), width=1, arrows=False)
        self.canvas.draw()


if __name__ == "__main__":

    line = Line('Green')
    file_path = os.path.abspath(os.path.join("system_data/lines", "green_line.xlsx"))
    line.load_track_blocks(file_path)
    
    app = QApplication(sys.argv)
    w = Window(line)
    w.show()

    sys.exit(app.exec())