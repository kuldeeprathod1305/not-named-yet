import osmnx as ox
import pickle
import os

os.makedirs("data", exist_ok=True)
print("Downloading Ahmedabad road network... (takes 1-2 min)")
G = ox.graph_from_place("Ahmedabad, India", network_type="drive")
with open("data/ahmedabad_graph.pkl", "wb") as f:
    pickle.dump(G, f)
print("Done! Saved to data/ahmedabad_graph.pkl")