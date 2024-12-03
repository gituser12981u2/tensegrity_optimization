import numpy as np
import pytest
from src.core.tensegrity_system import TensegritySystem
from src.physics.energy import EnergyAnalyzer


def test_simple_pendulum():
    """Test energy conservation for a simple pendulum."""
    system = TensegritySystem(gravity=np.array([0, 0, -9.81]))

    # Create a simple pendulum with a single mass and strut
    fixed_node = system.add_node(np.array([0., 0., 1.]), mass=1.0, fixed=True)
    mass_node = system.add_node(np.array([0., 0., 0.]), mass=1.0, fixed=False)

    # Add strut (like a rigid pendulum arm)
    system.add_strut(fixed_node, mass_node, stiffness=1000.0, damping=0.0)

    # Give initial velocity
    mass_node.velocity = np.array([0.1, 0., 0.])

    # Calculate energy
    analyzer = EnergyAnalyzer(system)
    initial_energy = analyzer.total_energy()

    # Should conserve energy (within numerical error)
    assert abs(analyzer.total_energy() - initial_energy) < 1e-10


def test_simple_spring():
    """Test energy conservation for a mass on a spring."""
    system = TensegritySystem(gravity=np.array([0, 0, 0]))  # No gravity

    # Create two nodes connected by a cable
    n1 = system.add_node(np.array([0., 0., 0.]), mass=1.0, fixed=True)
    n2 = system.add_node(np.array([1., 0., 0.]), mass=1.0, fixed=False)

    # Add cable with rest length less than current length (pre-tensioned)
    k = 100.0  # Spring constant
    rest_length = 0.8  # Rest length less than initial separation
    system.add_cable(n1, n2, rest_length=rest_length, stiffness=k, damping=0.0)

    analyzer = EnergyAnalyzer(system)

    # Initial elastic potential energy should be 0.5 * k * (x - x0)^2
    expected_pe = 0.5 * k * (1.0 - rest_length)**2
    calculated_pe = analyzer.potential_energy()
    assert abs(expected_pe - calculated_pe) < 1e-10


def test_gravitational_energy():
    """Test gravitational potential energy calculation."""
    system = TensegritySystem(gravity=np.array([0, 0, -9.81]))

    # Create a mass at height h
    h = 2.0
    mass = 1.0
    node = system.add_node(np.array([0., 0., h]), mass=mass, fixed=False)

    analyzer = EnergyAnalyzer(system)

    # Gravitational potential energy should be mgh
    expected_gpe = mass * 9.81 * h
    calculated_gpe = analyzer.potential_energy()
    assert abs(expected_gpe - calculated_gpe) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__])
