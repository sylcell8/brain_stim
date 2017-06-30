from utilities import get_uuid 
import copy as make_copy
import itertools
import numpy as np

# class QuerySet(set):
#     
#     def __init__(self, f):
#         self.query = f
#             
#     def __call__(self, x):
#         
#         return self.query(x)
#         
#     def filter_add(self, uuid, node):
#         if self(node): self.add(uuid)
# 
# class PositionOrganizer(object):
#     
#     def __init__(self, node_dict, position_key='position'):
#         pass
#     
#     def rebuild(self):
#         pass
    

class Network(object):
    
    def __init__(self, node_dict=None, edge_dict=None):
        
        # Set up nodes:
        if node_dict is None: self.node_dict = {}
        else: self.node_dict = node_dict
        
        # Set up edges:
        if edge_dict is None: self.edge_dict = {}
        else: self.edge_dict = edge_dict
        
#         # Set up node queries:
#         self.node_query_dict = {}
#         
#         # Set up kdtree:
#         self.position_organizer = PositionOrganizer(self.node_dict)
        
    def rebuild_position_tree(self):
        self.position_organizer.rebuild()
        
        
    def add_cross_product(self, **category_dict):
        
        common = category_dict.pop('common',{})
        uuid_list = []
        if len(category_dict) > 0:
            for node in (dict(itertools.izip(category_dict, x)) for x in itertools.product(*category_dict.itervalues())):
                node.update(common)
                uuid_list += self.add_node(node)
                
        return uuid_list
        
#     def add_node_query(self, query_name, f):
#         query_set = QuerySet(f)
#         self.node_query_dict[query_name] = query_set 
#         
#         for uuid, node in self.node_dict.items():
#             query_set.filter_add(uuid, node)
            
        
    def add_node(self, node={}, N=1):
        uuid_list = []
        for _ in xrange(N):
            uuid = get_uuid()
            uuid_list.append(uuid)
            self.node_dict[uuid] = make_copy.copy(node)
# 
#             # Build queries:
#             for query_set in self.node_query_dict.values():
#                 query_set.filter_add(uuid, self.node_dict[uuid])
            
        return uuid_list
    
    def add_edge(self, source_uuid, target_uuid, edge={}):
        self.edge_dict.setdefault((source_uuid, target_uuid),[]).append(edge)
        
    def filter_nodes(self, f):
        return dict((key, val) for key, val in self.node_dict.items() if f(val))
    
    def filter_edges(self, f):
        
        return_dict = {}
        for key, curr_edge_list in self.edge_dict.items():
            filtered_list = [val for val in curr_edge_list if f(val) == True]
            if len(filtered_list) > 0:
                return_dict[key] = filtered_list 
        return return_dict
    
    def apply_to_nodes(self, f, node_filter=lambda n:True):
        map(lambda x: f(x), filter(node_filter, self.nodes))
        return self
    
    def apply_to_edges(self, f, edge_filter=lambda n:True):
        map(lambda x: f(x), filter(edge_filter, self.edges))
        return self
    
    def connect(self, connection_function,
                      source_filter=lambda n: True, 
                      target_filter=lambda n: True, 
                      join_filter=lambda x, y: True):
        source_uuid_list = self.filter_nodes(source_filter)
        target_uuid_list = self.filter_nodes(target_filter)
        
        for source_uuid in source_uuid_list:
            for target_uuid in target_uuid_list:
                source_node = self.node_dict[source_uuid]
                target_node = self.node_dict[target_uuid]
                if join_filter(source_node, target_node):
                    curr_connection = connection_function(source_node, target_node)
                    if not curr_connection is None:
                        self.add_edge(source_uuid, 
                                      target_uuid,
                                      curr_connection)
                    
#     def clone(self, node_filter=lambda x:True, edge_filter=lambda x:True):
#         
#         old_uuid_to_new_dict = {}
#         new_node_dict = {}
#         for curr_old_uuid, curr_old_node_dict in self.filter_nodes(node_filter).items():
#             curr_new_uuid = get_uuid()
#             new_node_dict[curr_new_uuid] = make_copy.copy(curr_old_node_dict)
#             old_uuid_to_new_dict[curr_old_uuid] = curr_new_uuid 
# 
#         network = Network(node_dict= new_node_dict)
#         
#         for (curr_old_uuid_source, curr_old_uuid_target), curr_old_edge_list in self.filter_edges(edge_filter).items():
#             curr_new_uuid_source = old_uuid_to_new_dict[curr_old_uuid_source]
#             curr_new_uuid_target = old_uuid_to_new_dict[curr_old_uuid_target]
#             for curr_old_edge in curr_old_edge_list:
#                 network.add_edge(curr_new_uuid_source, curr_new_uuid_target, make_copy.copy(curr_old_edge))
#             
#         return network
#         
#     def merge(self, other_network):
#         
#         for key, node in other_network.node_dict.items():
#             assert not key in self.node_dict
#             self.node_dict[key] = node
#             
#         for key, edge in other_network.edge_dict.items():
#             assert not key in self.edge_dict
#             self.edge_dict[key] = edge
#         
#         return self
#     
#     def split(self, node_filter=lambda n:False, edge_filter=lambda e: False):
#         
#         new_network = Network()
#         
#         for key, node in self.node_dict.items():
#             if node_filter(node):
#                 new_network.node_dict[key] = self.node_dict.pop(key)
#                 
#         for key, edge in self.edge_dict.items():
#             if edge_filter(edge):
#                 new_network.edge_dict[key] = self.edge_dict.pop(key)
#         
#         return new_network
#     
#     def remove_dangling_edges(self):
#         dangling_edge_list = []
#         
#         for key in self.edge_dict.keys():
#             if key[0] is None or key[1] is None:
#                 dangling_edge_list.append(self.edge_dict.pop(key))
#                 
#         return dangling_edge_list
#     
#     def remove_unregistered_edges(self):
#         dangling_edge_list = []
#         
#         for key in self.edge_dict.keys():
#             if not key[0] in self.node_dict or not key[1] in self.node_dict:
#                 dangling_edge_list.append(self.edge_dict.pop(key))
#                 
#         return dangling_edge_list
#     
#     def create_sub_network(self, node_filter=lambda n:True, edge_filter=lambda e: True, remove_dangling_edges=True, remove_unregistered_edges=True):
#         
#         new_network = Network()
#         
#         for key, node in self.node_dict.items():
#             if node_filter(node):
#                 new_network.node_dict[key] = self.node_dict[key]
#                 
#         for key, edge in self.edge_dict.items():
#             if edge_filter(edge):
#                 new_network.edge_dict[key] = self.edge_dict[key]
#         
#         if remove_dangling_edges: new_network.remove_dangling_edges()
#         if remove_unregistered_edges: new_network.remove_unregistered_edges()
#         
#         return new_network
    
    @property
    def number_of_nodes(self):
        return len(self.node_dict)
    
    @property
    def number_of_edges(self):
        return reduce(lambda x, y:x+y, [len(x) for x in self.edge_dict.values()])
    
    def __str__(self):
        return_str = '======================\n'
        return_str += 'Nodes:\n'
        for key, val in self.node_dict.items():
            return_str += "%s %s\n" % (key, val)
    
        return_str += "Edges:\n"

        for key, val in self.edge_dict.items():
            return_str += "%s %s\n" % (key, val)
        return_str += '======================\n'
            
        return return_str
    
    def to_json(self):
        pass
    
    def to_df(self):
        pass
    
    def to_simvis(self):
        pass

    def to_dict(self):
        return {'nodes':self.node_dict, 'edges':self.edge_dict}
    
    def to_networkx(self):
        pass
    
        # # Create a networkx graph
        # import networkx as nx
        # G = nx.MultiDiGraph()
        # G.add_nodes_from(network.node_dict.items())
        # for (source_uuid, target_uuid), edge_list in network.edge_dict.items():
        #     for edge in edge_list:
        #         G.add_edge(source_uuid, target_uuid, attr_dict=edge)

    
    def __getitem__(self, key):
        return self.node_dict[key]
            
    @property
    def nodes(self):
        return self.node_dict.values()

    @property
    def edges(self):
        return reduce(lambda x, y: x+y, self.edge_dict.values())
        
         
        
    
    