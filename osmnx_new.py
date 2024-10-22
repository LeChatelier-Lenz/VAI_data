import networkx as nx
import osmnx as ox

# download/model a street network for some city then visualize it
G = ox.graph_from_place('New York, New York, USA', network_type='drive')
fig, ax = ox.plot_graph(G)

# convert graph to line graph so edges become nodes and vice versa
edge_centrality = nx.closeness_centrality(nx.line_graph(G))
nx.set_edge_attributes(G, edge_centrality, "edge_centrality")

# color edges in original graph with closeness centralities from line graph
ec = ox.plot.get_edge_colors_by_attr(G, "edge_centrality", cmap="inferno")
fig_1, ax_1 = ox.plot_graph(G, edge_color=ec, edge_linewidth=2, node_size=0)