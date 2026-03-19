import pickle
import networkx as nx
import osmnx as ox

_graph = None

def load_graph():
    global _graph
    if _graph is None:
        print("Loading road graph...")
        with open("data/ahmedabad_graph.pkl", "rb") as f:
            _graph = pickle.load(f)
        print("Graph ready.")
    return _graph

def get_route(source_coords, dest_coords, traffic_score=5.0, crowd_score=2.5):
    """
    source_coords: [lat, lon]
    dest_coords:   [lat, lon]
    Returns best route and alt route as lists of [lat, lon] pairs
    """
    G = load_graph()

    # Find nearest road nodes to the clicked points
    orig = ox.nearest_nodes(G, source_coords[1], source_coords[0])
    dest = ox.nearest_nodes(G, dest_coords[1], dest_coords[0])

    # Add congestion weight to every edge
    for u, v, data in G.edges(data=True):
        length = data.get("length", 50)
        data["weight"] = length + (traffic_score * 10) + (crowd_score * 5)

    try:
        # Best route — avoids congestion
        route = nx.shortest_path(G, orig, dest, weight="weight")
        coords = [[G.nodes[n]["y"], G.nodes[n]["x"]] for n in route]

        # Calculate real distance
        length_m = sum(
            G[u][v][0].get("length", 0)
            for u, v in zip(route[:-1], route[1:])
        )
        estimated_time = max(1, int((length_m / 1000) / 30 * 60))  # 30 km/h avg

        # Alt route — pure shortest distance, ignores congestion
        alt = nx.shortest_path(G, orig, dest, weight="length")
        alt_coords = [[G.nodes[n]["y"], G.nodes[n]["x"]] for n in alt]

    except nx.NetworkXNoPath:
        return {"best_route": [], "alt_route": [], "estimated_time": 0}

    return {
        "best_route": coords,
        "alt_route": alt_coords,
        "estimated_time": estimated_time
    }