import numpy as np
from typing import Dict, Callable
from src.core.tensegrity_system import TensegritySystem


class DynamicsSimulator:
    """Simulator for tensegrity system dynamics."""

    def __init__(self, system: TensegritySystem, dt: float = 0.01):
        self.system = system
        self.dt = dt
        self.time = 0.0
        # Additional forces by node ID
        self.external_forces: Dict[int, Callable] = {}

    def add_external_force(self, node_id: int,
                           force_func: Callable[[float], np.ndarray]):
        """Add an external force to a node as a function of a time."""
        self.external_forces[node_id] = force_func

    def step(self):
        """Perform step of the simulation using velocity Verlet integration."""
        forces = self.system.get_forces()

        # Add external forces
        for node_id, force_func in self.external_forces.items():
            if node_id < len(self.system.nodes):
                forces[node_id] += force_func(self.time)

        # First half of velocity Verlet
        for node in self.system.nodes:
            if not node.fixed:
                # Update position using current velocity and acceleration
                node.position += node.velocity * self.dt + 0.5 * \
                    node.acceleration * self.dt**2

                # Store current acceleration for velocity update
                old_acceleration = node.acceleration.copy()

                # Calculate new acceleration
                node.acceleration = forces[node.id] / node.mass

                # Update velocity using average of old and new acceleration
                node.velocity += 0.5 * \
                    (old_acceleration + node.acceleration) * self.dt

            self.time += self.dt

    def reset(self):
        """Reset the simulation to its initial conditions."""
        for node in self.system.nodes:
            node.velocity = np.zeros_like(node.position)
            node.acceleration = np.zeros_like(node.position)
        self.time = 0.0
