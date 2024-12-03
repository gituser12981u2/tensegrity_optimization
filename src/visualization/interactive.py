import pyvista as pv
from src.core.element import Cable
from src.core.tensegrity_system import TensegritySystem


class InteractiveVisualizer:
    """Interactive visualizer for tensegrity system."""

    def __init__(self, system: TensegritySystem):
        self.system = system
        self.plotter = pv.Plotter()
        self.node_actors = {}
        self.element_actors = {}

    def setup_plot(self):
        """Set up the interactive plotting environment."""
        self.plotter.set_background('white')
        self.plotter.add_axes()
        self.plotter.show_grid()

    def update_system(self):
        """Update the visualization with current system state."""
        # Update nodes
        for node in self.system.nodes:
            if node.id in self.node_actors:
                self.node_actors[node.id].points = node.position
            else:
                sphere = pv.Sphere(radius=0.05, center=node.position)
                self.node_actors[node.id] = self.plotter.add_mesh(
                    sphere, color='red' if node.fixed else 'black')

        # Update elements
        for element in self.system.cables + self.system.struts:
            if element.id in self.element_actors:
                line = pv.Line(element.node1.position, element.node2.position)
                self.element_actors[element.id].points = line.points
            else:
                line = pv.Line(element.node1.position, element.node2.position)
                color = 'red' if isinstance(element, Cable) else 'blue'
                self.element_actors[element.id] = self.plotter.add_mesh(
                    line, color=color, line_width=3)

    def show(self, interactive: bool = True):
        """Display the interactive visualization."""
        self.setup_plot()
        self.update_system()
        self.plotter.show(interactive_update=interactive)

    def close(self):
        """Close the visualization window."""
        self.plotter.close()
