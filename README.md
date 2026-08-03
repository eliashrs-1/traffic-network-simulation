# Urban Traffic Network Simulation

A computational modeling project simulating vehicle movement through an urban road network using graph theory, queueing theory, stochastic processes, and differential equation-based dispersal models.

## Project Overview

This project develops a simulation framework for studying traffic movement through an urban road network near Northeastern University.

The road system is represented as a graph, where intersections and roads are modeled as nodes and edges. Vehicles are generated as agents with randomly assigned destinations, and their movement through the network is simulated using mathematical and statistical models.

The project combines network modeling, queueing theory, and differential equations to analyze traffic behavior and estimate travel and dispersal times.

## Modeling Approach

The simulation incorporates several mathematical modeling techniques:

### Graph-Based Road Network Modeling

- Road networks are represented using graph structures.
- Geographic road data is converted into a computational network for simulation.

### Agent-Based Simulation

- Vehicles are modeled as individual agents moving through the network.
- Origins and destinations are randomly generated to simulate traffic demand.

### Queueing Theory

- Queueing methods are used to model congestion, delays, and interactions between vehicles moving through the network.

### Dispersal Differential Equation Modeling

- Ordinary differential equations (ODEs) are used to model dispersal behavior and measure how traffic spreads through the network over time.

### Event-Driven Simulation

- The simulation progresses through scheduled events that update vehicle positions and network states.

## Project Structure

```
.
├── __init__.py        # Main package initialization and model interface
├── sim.py             # Simulation engine and event handling
├── typing.py          # Data structures and type definitions
├── requirements.txt   # Python dependencies
└── pyrightconfig.json # Type checking configuration
```

## Technologies Used

- Python
- NumPy
- NetworkX
- OSMnx
- Shapely

## Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The simulation can be run by importing the package and creating a model from a geographic road network.

General workflow:

1. Generate a road network from geographic coordinates.
2. Convert the road network into a graph representation.
3. Initialize the simulation with a selected number of agents.
4. Simulate vehicle movement through the network.
5. Analyze traffic dispersion and travel times.

## Results and Analysis

The model provides a framework for studying:

- Vehicle movement through urban road networks
- Traffic dispersion over time
- Effects of network structure on travel behavior
- Simulated travel and dispersal times

## Background

This project was completed as part of a university computational modeling course project.

The work involved applying mathematical modeling techniques, including graph theory, queueing theory, stochastic simulation, and differential equations, to study transportation systems.

## Acknowledgements

This project was completed as a collaborative university computational modeling project. Development and analysis were performed as part of a team effort.
