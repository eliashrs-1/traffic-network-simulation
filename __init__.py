"""Meso- and microscopic models for traffic networks"""

__all__ = ["typing", "sim", "Model", "model_from_latlon", "init", "exec", "clear"]
__version__ = "0.1"
__author__ = ["J. Nolan Faught <nagefire.dev@gmail.com>", "Eli Rapkin-Stiles"]

from . import typing
from . import sim
from .typing import Model
import networkx as nx
import numpy.typing as npt


def clean_osmnx(G: nx.MultiDiGraph) -> nx.DiGraph:
    """Convert OSMnx network to NetworkX digraph and normalize attributes"""
    from shapely import geometry

    # renumber vertices
    D = {u: i + 1 for i, u in enumerate(G.nodes)}
    G = nx.relabel_nodes(G, D)

    # create graph structure
    res = nx.DiGraph()
    res.add_nodes_from(G.nodes())
    res.add_edges_from(G.edges())

    # copy metadata from vertices
    for u in G.nodes():
        res.nodes[u]["x"] = G.nodes[u]["x"]
        res.nodes[u]["y"] = G.nodes[u]["y"]

    # copy metadata from edges
    for u, v in G.edges():
        attr = G[u][v][0]

        # copy metadata from dictionary
        res[u][v]["osmid"] = attr["osmid"]
        res[u][v]["length"] = attr["length"]

        # set defaults for attributes that may not be present
        res[u][v]["name"] = ""
        res[u][v]["lanes"] = 1

        X = [
            [res.nodes[u]["x"], res.nodes[v]["y"]],
            [res.nodes[v]["x"], res.nodes[v]["y"]],
        ]
        res[u][v]["geometry"] = geometry.LineString(X)

        if "lanes" in attr:
            if isinstance(attr["lanes"], list):
                res[u][v]["lanes"] = int(attr["lanes"][0])
            else:
                res[u][v]["lanes"] = int(attr["lanes"])

        if "geometry" in attr:
            res[u][v]["geometry"] = attr["geometry"]

        if "name" in attr:
            res[u][v]["name"] = attr["name"]

    return res


def model_from_latlon(lat: npt.NDArray, lon: npt.NDArray, num_agents: int = 0):
    import osmnx
    from shapely import geometry

    poly = geometry.Polygon(zip(lon, lat))
    G = osmnx.graph_from_polygon(poly, network_type="drive_service")
    G = clean_osmnx(G)

    return Model(G, num_agents=num_agents)


def init(model: Model, occupancy: float = 0.2):
    from . import sim
    import numpy as np

    max_nagents = np.sum(model.capacity)

    sim.init_agents(model, int(occupancy * max_nagents))
    sim.init_events(model)


def exec(model: Model, t: float = 1000):
    """execute the model event loop for t seconds or until no more events occur"""
    from . import sim
    import heapq

    i = 0

    while len(model.events) > 0 and model.time < t:
        ev = heapq.heappop(model.events)
        d = sim.handle(model, ev[0], ev[1])
        print(f"{i}: t={ev[0]} event={ev[1]} res={d}")

        i += 1


def clear(model: Model):
    model.time = 0.0
    model.events = []
    model.num_agents = 0
    model.has_event[:] = False
    model.flow[:] = 0

    for obj in model.queue:
        obj.clear()


def plot_density(model: Model):
    import numpy as np
    import pandas as pd
    from plotly import express as px
    from plotly import graph_objects as go

    lon = np.array([attr["x"] for _, attr in model.G.nodes(data=True)])
    lat = np.array([attr["y"] for _, attr in model.G.nodes(data=True)])
    label = [f"{n}" for n in model.G.nodes]

    phi = np.array([len(obj) for obj in model.queue]) / model.capacity
    rho = (model.flow[:, 0] - model.flow[:, 1]) / 5.0
    lat = np.zeros(model.edgeset.shape[0])
    lon = np.zeros(model.edgeset.shape[0])

    for _, _, attr in model.G.edges(data=True):
        tmp1, tmp2 = attr["geometry"].xy
        ind = attr["ind"]
        k = len(tmp1) // 2
        lat[ind] = tmp2[k]
        lon[ind] = tmp1[k]

    df = pd.DataFrame({"lat": lat, "lon": lon, "heat": phi})
    fig = px.density_map(df, lat="lat", lon="lon", z="heat", zoom=14.8)

    fig.show()


def plot_network(model: Model):
    import numpy as np
    import pandas as pd
    from plotly import express as px
    from plotly import graph_objects as go

    fig = go.Figure()

    for _, _, attr in model.G.edges(data=True):
        lon, lat = attr["geometry"].xy
        ind = attr["ind"]

        c = "grey"

        fig.add_trace(
            go.Scattermap(
                lat=np.array(lat),
                lon=np.array(lon),
                mode="lines",
                line=dict(width=2, color=c),
                showlegend=False,
            )
        )

    lon = np.array([attr["x"] for _, attr in model.G.nodes(data=True)])
    lat = np.array([attr["y"] for _, attr in model.G.nodes(data=True)])
    label = [f"{n}" for n in model.G.nodes]

    fig.add_trace(go.Scattermap(lat=lat, lon=lon, text=label, showlegend=False))
    # px.scatter_map(lat=lat, lon=lon, hover_name=label, zoom=14.8)

    fig.show()
