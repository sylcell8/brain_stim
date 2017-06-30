import pandas as pd
import networkx as nx
from isee_engine.experimental.graph_model import create_kdtree, visualize, to_dict
import os
import h5py

input_dir = './'
target_cell_model_file_name = os.path.join(input_dir, 'cell_models.csv')
target_cell_file_name = os.path.join(input_dir, 'cells.csv')
connection_model_file_name = os.path.join(input_dir, 'connection_types.csv')
connection_file_name = os.path.join(input_dir, 'lgn2v1.h5')
input_cell_file_name = os.path.join(input_dir, 'lgn_cells.csv')
input_model_file_name = os.path.join(input_dir, 'lgn_cell_models.csv')

 
# Load source data:
source_cell_df = pd.read_csv(input_cell_file_name, sep=' ')
source_cell_model_df = pd.read_csv(input_model_file_name, sep=' ')
source_model_dict = {}
for _, row in source_cell_model_df.iterrows():
    model_id = row.pop('model_id')
    source_model_dict[model_id]=row.to_dict()
G_source = nx.MultiDiGraph()
for _, row in source_cell_df.iterrows():
    gid = row.pop('id')
    model_id = row.pop('model_id')
    G_source.add_node(gid, model_dict=source_model_dict[model_id], model_id=model_id, **row.to_dict())    
 
# Load target data:
target_cell_model_df = pd.read_csv(target_cell_model_file_name, sep=' ')
target_cell_df = pd.read_csv(target_cell_file_name, sep=' ')
target_model_dict = {}
for _, row in target_cell_model_df.iterrows():
    model_id = row.pop('model_id')
    target_model_dict[model_id]=row.to_dict()
G_target = nx.MultiDiGraph()
for _, row in target_cell_df.iterrows():
    gid = row.pop('id')
    model_id = row.pop('model_id')
    G_target.add_node(gid, model_dict=target_model_dict[model_id], model_id=model_id, **row.to_dict())

# Merge Source and target graphs:
G = nx.disjoint_union(G_source, G_target)
target_gid_offset = len(G_source)
  
# Load connection data from hdf5:
connection_model_df = pd.read_csv(connection_model_file_name, sep=' ')
connection_model_dict = {}
for _, row in connection_model_df.iterrows():
    src_label = row.pop('source_label')
    tgt_label = row.pop('target_label')
    connection_model_dict[src_label, tgt_label]=row.to_dict()
f = h5py.File(connection_file_name)
indptr = f['indptr'][:]
nsyn_dict, src_gids_dict = {}, {}
for tgt_gid_pre, (start_ind, end_ind) in enumerate(zip(indptr[:-1], indptr[1:])):
    tgt_gid = tgt_gid_pre + target_gid_offset
    tgt_label = G.node[tgt_gid]['model_dict']['type_label']
    nsyn_list = f['nsyns'][start_ind:end_ind]
    src_gid_list = f['src_gids'][start_ind:end_ind]
    connection_dict_list = [connection_model_dict[G.node[src_gid]['model_dict']['type_label'], tgt_label] for src_gid in src_gid_list]
    for src_gid, connection_dict, nsyn in zip(src_gid_list, connection_dict_list, nsyn_list):
        G.add_edge(src_gid, tgt_gid, connection_dict=connection_dict, nsyn=nsyn)
f.close()

# Query for neighbors of cell:
position_array, tree = create_kdtree(G)

print tree.query_ball_point(position_array[9000,:],1000)
visualize(G)

D = to_dict(G)

print len(D)

# import scipy.spatial as sps
# 
# data = np.random.rand(10,3)
# print data
# tree = sps.KDTree(data, leafsize=10)

# for source_gid, target_gid, nsyn in tmp:
#     src_label = G.node[source_gid]['model_dict']['type_label']
#     tgt_label = G.node[target_gid]['model_dict']['type_label']
#     print source_gid, target_gid, nsyn, src_label, tgt_label,  connection_model_dict[src_label, tgt_label]
#     
# 
# print connection_model_df.head(5)
# 
# for key, val in connection_model_dict.items():
#     print key, val





# Load dipde cortical column model:
# data_model = json.load(open('/local1/workspace/Sandbox/graph_representation/cortical_column.json', 'r'))
# network = Network(**data_model)
# 
# G = to_graph(network)
# 
# def strong_connection(u,v,d):
#     return d['nsyn'] > 2000.
# 
# def weak_connection(u,v,d):
#     return not strong_connection(u,v,d)
# 
# G2 = edge_select(G, strong_connection)
# G3 = edge_select(G, weak_connection)
# 
# plt.figure()
# visualize(G, show=False)
# plt.gca().set_xlim([0,16])
# plt.gca().set_ylim([0,16])
# 
# plt.figure()
# visualize(G2, show=False)
# plt.gca().set_xlim([0,16])
# plt.gca().set_ylim([0,16])
# 
# plt.figure()
# visualize(G3, show=False)
# plt.gca().set_xlim([0,16])
# plt.gca().set_ylim([0,16])
# 
# plt.show()


# print edge_list
# G = nx.MultiDiGraph(edge_list)
# print G.node[1]
# print G[1]

# for n in G:
#     print n

# print nx.info(G)
# print nx.degree(G)
# 
# visualize(G)
# plt.show()
# 
# nx.draw(G, nodecolor='r',edge_color='b')
# plt.show()


# 
# # Example query functions
# # Each assumes that it receives two nodes (u,v) and 
# # the data (d) for an edge 
# 
# def dog_feeling(u, v, d):
#     return (d['statementid'] == "3" 
#             and G2.node[u]['type'] == "Dog"
#             or G2.node[u]['type'] == "Dog")
# 
# def any_feeling(u,v,d):
#     return (d['statementid'] == "3" 
#             and G2.node[u]['type'] == "Feeling"
#             or G2.node[u]['type'] == "Feeling")
# 
# def cat_feeling(u,v,d):
#     return (G2.node[u]['type'] == "Cat"
#             or G2.node[v]['type'] == "Cat")
# 
# # Using the queries
# print select(G2, query = dog_feeling)
# print select(G2, query = any_feeling)
# print select(G2, query = cat_feeling)




# from isee_engine.popnet.io import population_list_to_csv

# G1 = nx.MultiDiGraph()
# G1.add_node(0)
# G1.add_node(1)
# 
# print id(G1[0])
# print id(G1[1]) 
# 
# G2 = nx.MultiDiGraph()
# G2.add_node(0)
# G2.add_node(1)
# 
# print id(G2[0])
# print id(G2[1])
# 
# # G3 = nx.compose(G1, G2)
# G3 = nx.disjoint_union(G1, G2)
# 
# for n in G3.nodes():
#     print id(G3[n])