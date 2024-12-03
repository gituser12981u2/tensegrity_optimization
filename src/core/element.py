import numpy as np
from dataclasses import dataclass
from .node import Node

EPSILON = 1e-10  # Small number to prevent division by zero


@dataclass
class Element:
    """Base class from tensegrity elements: cables or struts."""
    id: int
    node1: Node
    node2: Node
    rest_length: float
    stiffness: float
    damping: float = 0.1

    def length(self) -> float:
        """Calculate current length of the element."""
        delta = self.node2.position - self.node1.position
        length = np.linalg.norm(delta)

        # Prevent zero length
        return max(length, EPSILON)

    def direction(self) -> np.ndarray:
        """Unit vector from node1 to node2."""
        delta = self.node2.position - self.node1.position
        length = np.linalg.norm(delta)

        # Handle near-zero length case
        if length < EPSILON:
            # Return last known good direction or a default direction
            return np.array([1.0, 0.0, 0.0])[:len(delta)]

        return delta / length

    def relative_velocity(self) -> np.ndarray:
        """Calculate relative velocity between nodes."""
        return self.node2.velocity - self.node1.velocity

    def force(self) -> float:
        """
        Calculate force in the element.

            - positive for tension, negative for compression.
        """
        current_length = self.length()
        if current_length < EPSILON:
            return 0.0
        return self.stiffness * (current_length - self.rest_length)

    def force_vector(self) -> np.ndarray:
        """Calculate force vector acting on node2."""
        force_magnitude = self.force()
        direction = self.direction()
        return direction * force_magnitude

    def damping_force(self) -> np.ndarray:
        """Calculate damping force."""
        rel_vel = self.relative_velocity()
        direction = self.direction()

        # Computer damping force
        dapming_magnitude = self.damping * np.dot(rel_vel, direction)

        # Limit damping force to 10x the spring force to prevent instability
        max_damping = abs(self.force()) * 10
        dapming_magnitude = np.clip(
            dapming_magnitude, -max_damping, max_damping)

        return direction * dapming_magnitude


class Cable(Element):
    """Represents a tension only cable element."""

    def force(self) -> float:
        """Cables can only provide tension."""
        return max(0, super().force())


class Strut(Element):
    """Represents a compression only strut element."""

    def force(self) -> float:
        """Struts can only provide compression."""
        return min(0, super().force())
