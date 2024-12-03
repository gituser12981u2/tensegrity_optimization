# examples/dynamic_simulation.py
import numpy as np
import time
from src.core.tensegrity_system import TensegritySystem
from src.physics.dynamics import DynamicsSimulator, EnergyAnalyzer
from src.visualization.interactive import InteractiveVisualizer


def create_tensegrity_prism(height: float = 1.0, radius: float = 1.0):
    """Create a tensegrity prism with specified dimensions."""
    system = TensegritySystem()

    # Create top triangle
    n1 = system.add_node(np.array([radius, 0, height]))
    n2 = system.add_node(np.array([-radius/2, radius*0.866, height]))
    n3 = system.add_node(np.array([-radius/2, -radius*0.866, height]))

    # Create bottom triangle (rotated 30 degrees)
    n4 = system.add_node(np.array([radius*0.866, radius/2, 0]), fixed=True)
    n5 = system.add_node(np.array([-radius, 0, 0]), fixed=True)
    n6 = system.add_node(np.array([radius*0.134, -radius*0.5, 0]), fixed=True)

    # Add struts
    system.add_strut(n1, n5, stiffness=1000.0, damping=1.0)
    system.add_strut(n2, n6, stiffness=1000.0, damping=1.0)
    system.add_strut(n3, n4, stiffness=1000.0, damping=1.0)

    # Add cables with some initial tension
    tension_factor = 0.95  # Rest length is 90% of initial length

    # Top triangle cables
    for n_1, n_2 in [(n1, n2), (n2, n3), (n3, n1)]:
        rest_length = np.linalg.norm(
            n_2.position - n_1.position) * tension_factor
        system.add_cable(n_1, n_2, rest_length=rest_length,
                         stiffness=500.0, damping=0.5)

    # Bottom triangle cables
    for n_1, n_2 in [(n4, n5), (n5, n6), (n6, n4)]:
        rest_length = np.linalg.norm(
            n_2.position - n_1.position) * tension_factor
        system.add_cable(n_1, n_2, rest_length=rest_length,
                         stiffness=500.0, damping=0.5)

    # Connecting cables
    for n_1, n_2 in [(n1, n4), (n2, n5), (n3, n6)]:
        rest_length = np.linalg.norm(
            n_2.position - n_1.position) * tension_factor
        system.add_cable(n_1, n_2, rest_length=rest_length,
                         stiffness=500.0, damping=0.5)

    return system


def add_perturbation(system: TensegritySystem):
    """Add an initial velocity perturbation to the top nodes."""
    for node in system.nodes[:3]:  # First three nodes (top triangle)
        node.velocity = np.array([0.05, 0.05, 0])  # Small initial velocity


def run_interactive_simulation():
    # Create system and setup
    system = create_tensegrity_prism()
    simulator = DynamicsSimulator(system, dt=0.001)
    energy_analyzer = EnergyAnalyzer(system)
    visualizer = InteractiveVisualizer(system)

    # Add initial perturbation
    add_perturbation(system)

    # Setup visualization
    visualizer.setup_plot()

    # Initial energy
    initial_energy = energy_analyzer.total_energy()

    def update():
        """Callback function for updating the simulation."""
        # Run multiple physics steps per frame for better stability
        for _ in range(5):
            simulator.step()

        # Update visualization
        visualizer.update_system()

        # Print energy conservation
        current_energy = energy_analyzer.total_energy()
        energy_error = abs(current_energy - initial_energy) / initial_energy
        print(f"Time: {simulator.time:.3f}, Energy Error: {energy_error:.6f}")

        return True  # Keep the timer running

    # Add timer event using the correct method
    visualizer.plotter.add_timer_event(
        callback=update, interval=10)  # 10ms between updates

    # Start interactive visualization
    visualizer.show()


if __name__ == "__main__":
    run_interactive_simulation()
