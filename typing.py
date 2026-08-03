"""simulation type declarations"""

import dataclasses
import enum
import networkx as nx
import numpy as np
from typing import Dict


class EventType(enum.Enum):
    RECORD = 0
    LIGHT = 1
    NEUMANN = 2
    DIRICHLET = 3


@dataclasses.dataclass(order=True)
class Event:
    type: EventType
    data: Dict


@dataclasses.dataclass
class Agent:
    dst: int


class Model:
    """container for traffic flow model state"""

    def __init__(self, G, num_agents: int = 100, car_length: float = 5.0):
        import collections
        from numpy import typing as npt
        from typing import Dict, List, Tuple

        self.G = G
        self.time: float = 0.0
        self.car_length: float = car_length
        self.num_agents: int = 0
        self.min_path: Dict = nx.floyd_warshall(self.G, weight="length")
        self.events: List[Tuple[float, Event]] = []

        n = G.number_of_nodes()
        self.has_event: npt.NDArray = np.zeros(n, dtype=np.bool)

        m = G.number_of_edges()

        self.edgeset: npt.NDArray = np.array([[e[0], e[1]] for e in G.edges])

        for i, e in enumerate(self.edgeset):
            G[e[0]][e[1]]["ind"] = i

        self.capacity: npt.NDArray = np.array(
            [
                int(G[u][v]["length"] * G[u][v]["lanes"] / car_length)
                for u, v in self.edgeset
            ],
            dtype=np.uint64,
        )
        self.capacity = np.maximum(self.capacity, 1)
        self.flow: npt.NDArray = np.zeros((m, 2), dtype=np.uint64)
        self.queue: List[collections.deque] = [
            collections.deque([], int(n)) for n in self.capacity
        ]

        from . import sim

        sim.init_agents(self, num_agents)
        sim.init_events(self)


def save_model(model: Model, relpath: str):
    import pandas as pd
    import pathlib

    path = pathlib.Path(relpath)
    path.mkdir(parents=True, exist_ok=True)

    df = nx.to_pandas_edgelist(model.G)
    df.to_csv(f"{relpath}/edges.csv", index=False)

    tmp = [
        pd.DataFrame({**{"vert": node, **data}}, index=[i])
        for i, (node, data) in enumerate(model.G.nodes(data=True))
    ]
    df = pd.concat(tmp)
    df.to_csv(f"{relpath}/vertices.csv", index=False)


def load_model(relpath: str) -> Model:
    import pandas as pd

    G = nx.DiGraph()

    df = pd.read_csv(f"{relpath}/vertices.csv")
    G.add_nodes_from(df.vert)

    for _, row in df.iterrows():
        u = row["vert"]
        x = row["x"]
        y = row["y"]

        G.nodes[u]["x"] = x
        G.nodes[u]["y"] = y

    df = pd.read_csv(f"{relpath}/edges.csv")
    E = [(row.source, row.target) for _, row in df.iterrows()]
    G.add_edges_from(E)

    for _, row in df.iterrows():
        u = row["source"]
        v = row["target"]

        G[u][v]["osmid"] = row["osmid"]
        G[u][v]["name"] = row["name"]
        G[u][v]["lanes"] = row["lanes"]
        G[u][v]["length"] = row["length"]
        G[u][v]["curve"] = row["curve"]

    return Model(G)
