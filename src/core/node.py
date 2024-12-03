import numpy as np
from dataclasses import dataclass


@dataclass
class Node:
    """Represents a node in the tensegrity system."""
    id: int
    position: np.ndarray  # [x, y] for 2D or [x, y, z] for 3D
    mass: float = 1.0
    fixed: bool = False  # Whether the node is fixed in space
    velocity: np.ndarray = None
    acceleration: np.ndarray = None

    def __post_init__(self):
        self.position = np.array(self.position, dtype=float)
        if self.velocity is None:
            self.velocity = np.zeros_like(self.position)
        if self.acceleration is None:
            self.acceleration = np.zeros_like(self.position)

    def dimension(self) -> int:
        """Return the dimensionality of the node (2 or 3)."""
        return len(self.position)
