from dipde.examples.cortical_column import get_network, example
from dipde.internals.network import Network
from isee_engine.experimental.graph_model.popnet import dipde_network_to_graph
from isee_engine.experimental.graph_model import to_dict, visualize

network = get_network() 

G = dipde_network_to_graph(network)
visualize(G, markersize=10)
D = to_dict(G)
 
round_trip_network = Network(**D)
example(show=True, network=round_trip_network)