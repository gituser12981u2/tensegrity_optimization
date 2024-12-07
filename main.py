import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from src.core.tensegrity_system import TensegritySystem
from src.physics.dynamics import DynamicsSimulator
from src.physics.energy import EnergyAnalyzer


def create_tensegrity_prism(height: float = 1.0, radius: float = 1.0):
    """Create a tensegrity prism with specified dimensions."""
    system = TensegritySystem()

    # Create top triangle with very light masses for better stability
    n1 = system.add_node(np.array([radius, 0, height]), mass=0.01)
    n2 = system.add_node(
        np.array([-radius/2, radius*0.866, height]), mass=0.01)
    n3 = system.add_node(
        np.array([-radius/2, -radius*0.866, height]), mass=0.01)

    # Create bottom triangle (rotated 30 degrees, fixed)
    n4 = system.add_node(
        np.array([radius*0.866, radius/2, 0]), mass=1.0, fixed=True)
    n5 = system.add_node(np.array([-radius, 0, 0]), mass=1.0, fixed=True)
    n6 = system.add_node(
        np.array([radius*0.134, -radius*0.5, 0]), mass=1.0, fixed=True)

    # Add struts with moderate stiffness and higher damping
    system.add_strut(n1, n5, stiffness=50.0, damping=2.0)
    system.add_strut(n2, n6, stiffness=50.0, damping=2.0)
    system.add_strut(n3, n4, stiffness=50.0, damping=2.0)

    # Add cables with less tension
    tension_factor = 0.99  # Even less initial tension

    # Top triangle cables
    for n_1, n_2 in [(n1, n2), (n2, n3), (n3, n1)]:
        rest_length = np.linalg.norm(
            n_2.position - n_1.position) * tension_factor
        system.add_cable(n_1, n_2, rest_length=rest_length,
                         stiffness=25.0, damping=2.0)

    # Bottom triangle cables
    for n_1, n_2 in [(n4, n5), (n5, n6), (n6, n4)]:
        rest_length = np.linalg.norm(
            n_2.position - n_1.position) * tension_factor
        system.add_cable(n_1, n_2, rest_length=rest_length,
                         stiffness=25.0, damping=2.0)

    # Connecting cables
    for n_1, n_2 in [(n1, n4), (n2, n5), (n3, n6)]:
        rest_length = np.linalg.norm(
            n_2.position - n_1.position) * tension_factor
        system.add_cable(n_1, n_2, rest_length=rest_length,
                         stiffness=25.0, damping=2.0)

    return system


def add_perturbation(system: TensegritySystem):
    """Add a very small initial velocity perturbation to the top nodes."""
    for node in system.nodes[:3]:  # First three nodes (top triangle)
        node.velocity = np.array([0.0001, 0.0001, 0])


class TensegrityAnimation:
    def __init__(self, timesteps=5000, dt=0.000001):
        """Initialize the animation."""
        self.system = create_tensegrity_prism()
        self.simulator = DynamicsSimulator(self.system, dt=dt)
        self.energy_analyzer = EnergyAnalyzer(self.system)
        self.timesteps = timesteps

        add_perturbation(self.system)

        # Create figure with three subplots
        self.fig = plt.figure(figsize=(15, 5))
        self.ax1 = self.fig.add_subplot(131, projection='3d')
        self.ax2 = self.fig.add_subplot(132)
        self.ax3 = self.fig.add_subplot(133)

        # Initialize storage for energy plots
        self.times = []
        self.energy_errors = []
        self.energy_components = []
        self.initial_energy = self.energy_analyzer.total_energy()

        # Initialize plots
        self.cable_lines = []
        self.strut_lines = []
        self.energy_error_line, = self.ax2.plot([], [], 'b-')
        self.energy_components_lines = {
            'kinetic': self.ax3.plot([], [], 'r-', label='Kinetic')[0],
            'gravitational': self.ax3.plot([], [], 'g-', label='Gravitational')[0],
            'elastic': self.ax3.plot([], [], 'b-', label='Elastic')[0]
        }

        # Set up axes
        self.ax1.set_title('Tensegrity System')
        self.ax2.set_title('Energy Error')
        self.ax3.set_title('Energy Components')

        self.ax2.set_xlabel('Time')
        self.ax2.set_ylabel('Relative Energy Error')
        self.ax2.set_yscale('log')
        self.ax2.grid(True)

        self.ax3.set_xlabel('Time')
        self.ax3.set_ylabel('Energy')
        self.ax3.legend()
        self.ax3.grid(True)

        # Set fixed limits for 3D plot
        self.ax1.set_xlim([-2, 2])
        self.ax1.set_ylim([-2, 2])
        self.ax1.set_zlim([0, 2])

        # Create initial plot elements
        for cable in self.system.cables:
            line, = self.ax1.plot([], [], [], 'r--')
            self.cable_lines.append(line)
        for strut in self.system.struts:
            line, = self.ax1.plot([], [], [], 'b-')
            self.strut_lines.append(line)

        plt.tight_layout()

    def update(self, frame):
        """Update function for animation."""
        # Run multiple smaller steps for stability
        for _ in range(5):
            self.simulator.step()

        # Update cable positions
        for i, cable in enumerate(self.system.cables):
            pos1, pos2 = cable.node1.position, cable.node2.position
            self.cable_lines[i].set_data(
                [pos1[0], pos2[0]], [pos1[1], pos2[1]])
            self.cable_lines[i].set_3d_properties([pos1[2], pos2[2]])

        # Update strut positions
        for i, strut in enumerate(self.system.struts):
            pos1, pos2 = strut.node1.position, strut.node2.position
            self.strut_lines[i].set_data(
                [pos1[0], pos2[0]], [pos1[1], pos2[1]])
            self.strut_lines[i].set_3d_properties([pos1[2], pos2[2]])

        # Update energy plots
        current_time = self.simulator.time
        energy_dist = self.energy_analyzer.energy_distribution()

        self.times.append(current_time)
        energy_error = abs(
            energy_dist['total'] - self.initial_energy) / self.initial_energy
        self.energy_errors.append(energy_error)
        self.energy_components.append(energy_dist)

        # Update energy error plot
        self.energy_error_line.set_data(self.times, self.energy_errors)
        self.ax2.relim()
        self.ax2.autoscale_view()

        # Update energy components plot
        for key, line in self.energy_components_lines.items():
            line.set_data(self.times, [e[key] for e in self.energy_components])
        self.ax3.relim()
        self.ax3.autoscale_view()

        # Print progress occasionally
        if frame % 100 == 0:
            print(f"Step {frame}/{self.timesteps}, Time: {current_time:.3f}")
            print(f"Energy Error: {energy_error:.6f}")
            print(f"Energy Components: KE={energy_dist['kinetic']:.6f}, "
                  f"GPE={energy_dist['gravitational']:.6f}, "
                  f"EPE={energy_dist['elastic']:.6f}")
            print("---")

        return (self.cable_lines + self.strut_lines +
                [self.energy_error_line] +
                list(self.energy_components_lines.values()))

    def animate(self):
        """Create and save the animation."""
        anim = FuncAnimation(
            self.fig,
            self.update,
            frames=self.timesteps,
            interval=1,
            blit=True
        )
        plt.show()
        return anim


if __name__ == "__main__":
    animation = TensegrityAnimation()
    animation.animate()
