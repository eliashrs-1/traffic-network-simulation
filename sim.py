"""internal functions for simulation initialization and execution"""

from scipy import sparse as sp
from .typing import Agent, Event, EventType, Model


def handle(model: Model, t: float, event: Event):
    # update simulation time
    model.time = t

    match event.type:
        case EventType.RECORD:
            return dispatch_record(model, t, event.data["rate"])
        case EventType.LIGHT:
            return dispatch_light(model, t, event.data["vert"])
        case EventType.NEUMANN:
            return
        case EventType.DIRICHLET:
            return


def dispatch_record(model: Model, t: float, rate: float):
    import heapq

    heapq.heappush(model.events, (t + rate, Event(EventType.RECORD, {"rate": rate})))


def dispatch_light(model: Model, t: float, u: int):
    import heapq
    import numpy as np

    # FIXME: should not be possible to initialize agents at the boundary
    if model.G.out_degree(u) == 0:
        model.has_event[u] = False
        I = np.array([model.G[x][u]["ind"] for x in model.G.predecessors(u)])

        for i in I:
            model.num_agents -= len(model.queue[i])
            model.queue[i].clear()

        return

    # get neighbors and indices in model parameters
    links = np.array([*model.G.successors(u)])
    ind = np.array([model.G[u][v]["ind"] for v in links])

    # check for traffic jam
    mask = np.array([len(model.queue[i]) < model.queue[i].maxlen for i in ind])
    links = links[mask]
    ind = ind[mask]

    if not np.any(mask):
        heapq.heappush(model.events, (t + 3, Event(EventType.LIGHT, {"vert": u})))

        return

    # determine whether to add events for links and source
    ev_src = False
    ev_dst = np.zeros_like(links, dtype=np.bool)
    res = -1

    # loop over incoming links
    for x in model.G.predecessors(u):
        e = model.G[x][u]["ind"]

        if len(model.queue[e]) == 0:
            continue

        # get agent and current distance from target
        agent = model.queue[e][0]
        dist = model.min_path[u][agent.dst]
        res = max(res, dist)

        # get distance to target from roads
        link_dist = np.array([model.min_path[v][agent.dst] for v in links])
        i = np.argmin(link_dist)

        # case 1: we are as close as we can get to the target
        if np.all(mask) and link_dist[i] >= dist:
            model.queue[e].pop()
            model.num_agents -= 1
        # case 2: we can get closer to the target
        elif link_dist[i] < dist:
            model.queue[e].pop()
            model.queue[ind[i]].append(agent)

            ev_dst[i] = True

        ev_src |= len(model.queue[e]) > 0

    # create event for source
    if ev_src:
        heapq.heappush(model.events, (t + 3.0, Event(EventType.LIGHT, {"vert": u})))
    else:
        model.has_event[u - 1] = False

    # create events for neighbors
    mask = ev_dst & np.logical_not(model.has_event[links - 1])
    links = links[mask]

    for v in links:
        s = t + model.G[u][v]["length"] / 11.2
        heapq.heappush(model.events, (s, Event(EventType.LIGHT, {"vert": v})))

    model.has_event[links - 1] = True

    return res


def init_agents(model: Model, num_agents: int):
    """add agents to the model"""
    import numpy.random as rand

    m = model.edgeset.shape[0]
    n = model.G.number_of_nodes()
    dst = rand.randint(1, high=n + 1, size=num_agents)
    link = rand.randint(0, high=m, size=num_agents)

    for i in range(0, num_agents):
        e = link[i]

        if len(model.queue[e]) == model.queue[e].maxlen:
            continue
        else:
            model.queue[e].append(Agent(dst[i]))
            model.num_agents += 1


def init_events(model: Model):
    """create events based on agents in links"""
    import heapq
    import numpy as np
    from numpy import random as rand

    heapq.heappush(model.events, (0, Event(EventType.RECORD, {"rate": 5})))
    # get links that need events
    mask = np.array([len(obj) > 0 for obj in model.queue])

    # get dst vertices of these links
    U = model.edgeset[mask, 1]
    U = np.unique(U)
    n = len(U)
    t = rand.random(n) * 3

    # create events
    for i in range(0, n):
        heapq.heappush(model.events, (t[i], Event(EventType.LIGHT, {"vert": U[i]})))

    # update event link
    model.has_event[U - 1] = True
