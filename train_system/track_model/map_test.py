import sys
import networkx as nx
from matplotlib.figure import Figure
import matplotlib.pyplot as mpl
import matplotlib
matplotlib.use('QtAgg')

from PyQt6.QtWidgets import QWidget, QLayout, QApplication, QVBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.graph = nx.DiGraph()
        self.fig = mpl.figure()
        self.canvas = FigureCanvasQTAgg(self.fig)

        lo = QVBoxLayout()
        lo.addWidget(self.canvas)
        self.setLayout(lo)

        edges = [("1", "2"), ("1", "3"), ("2", "5"), ("3", "4"), ("3", "6"), ("5", "6"), ("4", "1")]

        self.fig.clear()
        self.graph.add_edges_from(edges)
        self.map = nx.planar_layout(self.graph)
        nx.draw_networkx_nodes(self.graph, self.map, node_size=3, node_color="Black")
        nx.draw_networkx_edges(self.graph, self.map, self.graph.edges(), width=3, arrows=False)
        #self.canvas.draw()
        


if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = Window()
    w.show()

    sys.exit(app.exec())