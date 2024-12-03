import numpy as np
import matplotlib.pyplot as plt
from src.core.tensegrity_system import TensegritySystem


class StaticVisualizer:
    """Static visualizer for tensegrity system."""

    def __init__(self, system: TensegritySystem):
        self.system = system
        self.fig = None
        self.ax = None

    def setup_plot(self):
        """Set up the plotting environment."""
        self.fig = plt.figure(figsize=(10, 10))
        if self.system.dimension() == 3:
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax = self.fig.add_subplot(111)

        # Set equal aspect ratio
        if self.system.dimension() == 2:
            self.ax.set_aspect('equal')
        else:
            # Equal aspect ratio for 3d plots
            self.ax.set_box_aspect([1, 1, 1])

    def plot_system(self, show_forces: bool = True):
        """Plot the tensegrity system."""
        if self.fig is None:
            self.setup_plot()

        self._plot_nodes()
        self._plot_elements()
        self._set_labels()

    def _plot_nodes(self):
        """Plot system nodes."""
        positions = np.array([node.position for node in self.system.nodes])
        colors = ['red' if node.fixed else 'black' for node in self.system.nodes]

        if self.system.dimension() == 3:
            self.ax.scatter(positions[:, 0], positions[:, 1],
                            positions[:, 2], c=colors, s=50)
        else:
            self.ax.scatter(positions[:, 0], positions[:, 1], c=colors, s=50)

    def _plot_elements(self):
        """Plot system elements."""
        for cable in self.system.cables:
            self._plot_element(cable, 'red', '--')
        for strut in self.system.struts:
            self._plot_element(strut, 'blue', '-')

    def _plot_element(self, element, color: str, style: str):
        """Plot a single element."""
        pos1, pos2 = element.node1.position, element.node2.position
        if self.system.dimension() == 3:
            self.ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], [
                         pos1[2], pos2[2]], color=color, linestyle=style)
        else:
            self.ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]],
                         color=color, linestyle=style)

    def _set_labels(self):
        """Set plot labels and title."""
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        if self.system.dimension() == 3:
            self.ax.set_zlabel('Z')
        self.ax.set_title('Tensegrity System')

    def show(self):
        """Display the plot."""
        plt.show()
