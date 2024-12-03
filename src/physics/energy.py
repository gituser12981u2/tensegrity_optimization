import numpy as np
from src.core.element import Cable, Strut
from src.core.tensegrity_system import TensegritySystem


class EnergyAnalyzer:
    """Analyzes energy components of the tensegrity system."""

    def __init__(self, system: TensegritySystem):
        self.system = system

    def kinetic_energy(self) -> float:
        """Calculate the total kinetic energy of the system."""
        ke = 0.0
        for node in self.system.nodes:
            if not node.fixed:
                velocity_squared = np.dot(node.velocity, node.velocity)
                if velocity_squared > 1e-10:  # Ignore very small velocities
                    ke += 0.5 * node.mass * velocity_squared

        return ke

    def gravitational_potential_energy(self) -> float:
        """Calculate the gravitational potential energy."""
        gpe = 0.0
        if self.system._dimension is not None:
            g_magnitude = np.linalg.norm(self.system.gravity)
            if g_magnitude > 1e-10:  # Only if gravity is non zero
                for node in self.system.nodes:
                    if not node.fixed:
                        # Height is the dot product with normalized gravity vector
                        g_direction = self.system.gravity / g_magnitude
                        height = np.dot(node.position, -g_direction)
                        gpe += node.mass * g_magnitude * height
        return gpe

    def elastic_potential_energy(self) -> float:
        """Calculate the elastic potential energy in cables and struts."""
        epe = 0.0

        for element in self.system.cables + self.system.struts:
            current_length = element.length()
            delta_l = current_length - element.rest_length

            # For cables, only count tension energy
            if isinstance(element, Cable) and delta_l > 0:
                epe += 0.5 * element.stiffness * delta_l**2
            # For struts, only count compression energy
            elif isinstance(element, Strut) and delta_l < 0:
                epe += 0.5 * element.stiffness * delta_l**2

        return epe

    def potential_energy(self) -> float:
        """Calculate the total potential energy of the system."""
        return self.gravitational_potential_energy() \
            + self.elastic_potential_energy()

    def total_energy(self) -> float:
        """Calculate the total energy of the system."""
        ke = self.kinetic_energy()
        pe = self.potential_energy()

        # Add small numerical stability checks
        if abs(ke) < 1e-10:
            ke = 0.0
        if abs(pe) < 1e-10:
            pe = 0.0

        return ke + pe

    def energy_distribution(self) -> dict:
        """Construct an overview of energy components."""
        return {
            'kinetic': self.kinetic_energy(),
            'gravitational': self.gravitational_potential_energy(),
            'elastic': self.elastic_potential_energy(),
            'total': self.total_energy()
        }
