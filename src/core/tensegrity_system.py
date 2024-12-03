import numpy as np
from typing import List, Optional
from src.core.element import Cable, Strut
from src.core.node import Node


class TensegritySystem:
    """Represents a complete tensegrity system."""

    def __init__(self, gravity: np.ndarray = None):
        self.nodes: List[Node] = []
        self.cables: List[Cable] = []
        self.struts: List[Strut] = []
        self._dimension: Optional[int] = None
        self.gravity = gravity if gravity is not None else np.array([
            0, 0, -9.81])

    def add_node(self, position: np.ndarray, mass: float = 1.0,
                 fixed: bool = False) -> Node:
        """Add a node to the system.

        Args:
            position (np.ndarray): Position vector of the node
            mass (float): mass of the node (default: 1.0)
            fixed (bool): Whether the node is fixed in space (default: False)

        Returns:
            Node: The created node
        """
        if self._dimension is None:
            self._dimension = len(position)
        elif len(position) != self._dimension:
            raise ValueError(f"Node position must be {self._dimension}D")

        node = Node(len(self.nodes), position, mass=mass, fixed=fixed)
        self.nodes.append(node)
        return node

    def add_cable(self, node1: Node, node2: Node,
                  rest_length: Optional[float] = None,
                  stiffness: float = 1.0, damping: float = 0.1) -> Cable:
        """
        Add a cable between two nodes.

        Args:
            node1 (Node): First node
            node2 (Node): Second node
            rest_length (Optional[float]): Rest length of cable (default: none, uses current distance)
            stiffness (float): Spring stiffness of cable (default: 1.0)
            damping (float): Damping coefficient (default: 0.1)
        """
        if rest_length is None:
            rest_length = np.linalg.norm(node2.position - node1.position)

        cable = Cable(len(self.cables), node1, node2,
                      rest_length, stiffness, damping)
        self.cables.append(cable)
        return cable

    def add_strut(self, node1: Node, node2: Node,
                  rest_length: Optional[float] = None,
                  stiffness: float = 1.0, damping: float = 0.1) -> Strut:
        """
        Add a strut between two nodes.

        Args:
            node1 (Node): First node
            node2 (Node): Second node
            rest_length (Optional[float]): Rest length of strut (default: none, uses current distance)
            stiffness (float): Spring stiffness of strut (default: 1.0)
            damping (float): Damping coefficient (default: 0.1)
        """
        if rest_length is None:
            rest_length = np.linalg.norm(node2.position - node1.position)

        strut = Strut(len(self.struts), node1, node2,
                      rest_length, stiffness, damping)
        self.struts.append(strut)
        return strut

    def dimension(self) -> int:
        """Return the dimensionality of the system."""
        return self._dimension if self._dimension is not None else 0

    def get_forces(self) -> dict:
        """Calculate all forces acting on each node."""
        forces = {node.id: np.zeros_like(node.position) for node in self.nodes}

        # Add gravitational forces
        if self._dimension is not None:  # Only add gravity if dimension is set
            for node in self.nodes:
                if not node.fixed:
                    gravity_force = self.gravity[:self._dimension]
                    forces[node.id] += node.mass * gravity_force

        # Add element forces
        for element in self.cables + self.struts:
            force = element.force() * element.direction()
            damp_force = element.damping_force()

            # Apply forces to both nodes (action-reaction)
            forces[element.node1.id] -= force + damp_force
            forces[element.node2.id] += force + damp_force

        return forces
