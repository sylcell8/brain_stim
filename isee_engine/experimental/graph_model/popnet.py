import dipde.internals.network as dipde_network_module
dipde_network_module_name = dipde_network_module.__name__
from isee_engine.experimental.graph_model import to_dict, from_dict
from isee_engine.experimental.graph_model import from_dict

from local1.workspace.isee_engine.nicholasc import network as nx

def dipde_network_to_graph(network):

    data_model = network.to_dict()
    G = from_dict(data_model)
    return G

def to_network_dict(G):
    
    D = to_dict(G)
    D['class'] = 'Network'
    D['module'] = dipde_network_module_name 