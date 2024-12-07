# Overview

This Tensegrity program aims to visualize a tensegrity system dynamically in order to optimize to its general geometric structure for both dynamic loads and extending resistance to failure at points.

This simulator includes:

- Dynamic simulation with verlet evolution
- Energy conservation analysis
- Real-time 3D visualization with matplotlib animate
- Material property consideration for the cables and struts
- Physical constraint enforcement.

## Physics Model

The simulator uses steel cables with a stiffness of 2000 N/m, and a maximum tension of 2000N and aluminum struts with a stiffness of 1000 N/m and a maximum compression of 1000N.

The system tracks three different types of energy: kinetic energy, gravitational potential energy, and elastic potential energy.

### Color coding

- Red dashed lines: Cables (tension elements)
- Blue solid lines: Struts (compression elements)
- Black dots: Nodes

Due to limited time, I did not have time to implement optimization path formulas that dynamically change the geometric structure of the tensegrity system. This program merely acts as a dynamic simulation of a tensegrity system and can be used to show how they work and how energy evolves over time in a static tensegrity system, or how the system acts when perturbed as a certain point. It can also be used to create any tensegrity system, by customizing the arrangement of nodes and cable and struct connections and see how the energy analysis changes and if the tensegrity structure remains static.
