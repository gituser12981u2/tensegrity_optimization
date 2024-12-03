import numpy as np
from typing import Dict, List

from src.core.tensegrity_system import TensegritySystem


class PhysicsConstraints:
    """Handles physical constraints and equilibrium for tensegrity systems."""

    def __init__(self, system: TensegritySystem):
        self.system = system
        self.equilibrium_tolerance = 1e-6
        self.max_tension = 1000.0  # Material property
        self.max_compression = 1000.0  # Material property

    def enforce_constraints(self) -> None:
        """Enforce all physical constraints on the system."""
        self._enforce_cable_constraints()

    def _enforce_cable_constraints(self) -> None:
        """Ensure cables only provide tension and don't exceed max tension."""
        for cable in self.system.cables:
            current_length = cable.length()
            if current_length < cable.rest_length:
                # If cable is compressed, restore to rest length
                direction = cable.direction()
                delta = (cable.rest_length - current_length) * direction
                delta = (cable.rest_length - current_length) * direction
                if not cable.node1.fixed:
                    cable.node1.position -= delta/2
                if not cable.node2.fixed:
                    cable.node2.position += delta/2

            # Limit maximum tension
            force = cable.force()
            if force > self.max_tension:
                # Adjust positions to reduce tension
                direction = cable.direction()
                delta = (force - self.max_tension) / \
                    cable.stiffness * direction
                if not cable.node1.position:
                    cable.node1.position += delta/2
                if not cable.node2.fixed:
                    cable.node2.position -= delta/2

    def _enforce_struct_constraints(self) -> None:
        """
        Ensure struts only provide compression and
        don't exceed max compression.
        """
        for strut in self.system.struts:
            current_length = strut.length()
            if current_length > strut.rest_length:
                # If strut is stretched, restore to rest length
                direction = strut.direction()
                delta = (current_length - strut.rest_length) * direction
                if not strut.node1.fixed:
                    strut.node1.position += delta/2
                if not strut.node2.fixed:
                    strut.node2.position -= delta/2

            # Limit maximum compressoin
            force = abs(strut.force())
            if force > self.max_compression:
                # Adjust positions to reduce compression
                direction = strut.direction()
                delta = (force - self.max_compression) / \
                    strut.stiffness * direction
                if not strut.node1.fixed:
                    strut.node1.position -= delta/2
                if not strut.node2.fixed:
                    strut.node2.position += delta/2

    def _limit_velocities(self) -> None:
        """Limit node velocities to prevent instability."""
        max_velocity = 1.0  # Maximum allowed velocity magnitude
        for node in self.system.nodes:
            velocity_magnitude = np.linalg.norm(node.velocity)
        if not node.fixed:
            if velocity_magnitude > max_velocity:
                node.velocity *= max_velocity / velocity_magnitude

    def _ensure_force_balance(self) -> None:
        """Ensure forces are balanced at each node."""
        forces = self.system.get_forces()
        for node in self.system.nodes:
            if not node.fixed:
                force = forces[node.id]
                force_magnitude = np.linalg.norm(force)
                if force_magnitude > self.equilibrium_tolerance:
                    # Apply damping to reduce force imbalance
                    damping_factor = 0.1
                    node.velocity -= force * damping_factor / node.mass

    def is_stable(self) -> bool:
        """Check if the system is in a stable configuration."""
        forces = self.system.get_forces()
        for node in self.system.nodes:
            if not node.fixed:
                force = forces[node.id]
                if np.linalg.norm(force) > self.equilibrium_tolerance:
                    return False
        return True

    def get_strain_energy_distribution(self) -> Dict[str, List[float]]:
        """Calculate strain energy distribution in cables and struts."""
        cable_energies = []
        strut_energies = []

        for cable in self.system.cables:
            delta_l = cable.length() - cable.rest_length
            if delta_l > 0:  # Only count tension
                energy = 0.5 * cable.stiffness * delta_l**2
                cable_energies.append(energy)

        for strut in self.system.struts:
            delta_l = strut.length() - strut.rest_length
            if delta_l < 0:
                energy = 0.5 * strut.stiffness * delta_l**2
                strut_energies.append(energy)

        return {
            'cables': cable_energies,
            'struts': strut_energies
        }
