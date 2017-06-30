import pandas as pd
import networkx as nx
from isee_engine.experimental.graph_model import create_kdtree, visualize, to_dict
import os
import h5py
from uuid import uuid4

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
source_gid_to_uuid_dict = {}
for gid, row in source_cell_df.iterrows():
    curr_uuid = str(uuid4())
    source_gid_to_uuid_dict[gid] = curr_uuid 
    model_id = row.pop('model_id')
    G_source.add_node(curr_uuid, model_dict=source_model_dict[model_id], model_id=model_id, coordinate_list=['LGd', gid], **row.to_dict())    

# Load target data:
target_cell_model_df = pd.read_csv(target_cell_model_file_name, sep=' ')
target_cell_df = pd.read_csv(target_cell_file_name, sep=' ')
target_model_dict = {}
for _, row in target_cell_model_df.iterrows():
    model_id = row.pop('model_id')
    target_model_dict[model_id]=row.to_dict()
G_target = nx.MultiDiGraph()
target_gid_to_uuid_dict = {}
for gid, row in target_cell_df.iterrows():
    curr_uuid = str(uuid4())
    target_gid_to_uuid_dict[gid] = curr_uuid
    model_id = row.pop('model_id')
    G_target.add_node(curr_uuid, model_dict=target_model_dict[model_id], model_id=model_id, coordinate_list=['V1', gid], **row.to_dict())
 
# Merge Source and target graphs:
G = nx.union(G_source, G_target)
for curr_coordinate_list in nx.get_node_attributes(G, 'coordinate_list').values():
    curr_coordinate_list.insert(0, 'G')

   
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
for tgt_gid, (start_ind, end_ind) in enumerate(zip(indptr[:-1], indptr[1:])):
    tgt_uuid = target_gid_to_uuid_dict[tgt_gid]
    tgt_label = G.node[tgt_uuid]['model_dict']['type_label']
    nsyn_list = f['nsyns'][start_ind:end_ind]
    src_gid_list = f['src_gids'][start_ind:end_ind]
    connection_dict_list = [connection_model_dict[G.node[source_gid_to_uuid_dict[src_gid]]['model_dict']['type_label'], tgt_label] for src_gid in src_gid_list]
    for src_gid, connection_dict, nsyn in zip(src_gid_list, connection_dict_list, nsyn_list):
        src_uuid = source_gid_to_uuid_dict[src_gid]
        G.add_edge(src_uuid, tgt_uuid, connection_dict=connection_dict, nsyn=nsyn)
f.close()
# 
# # Query for neighbors of cell:
# position_array, tree = create_kdtree(G)
# 
# print tree.query_ball_point(position_array[9000,:],1000)
# print nx.get_node_attributes(G, 'coordinate_list').items()

# for x in nx.get_node_attributes(G, 'coordinate_list').items():
#     print x

nodelist = zip(*sorted(nx.get_node_attributes(G, 'coordinate_list').items(), key=lambda x: tuple(x[1])))[0]
# for x in nodelist:
#     print x

visualize(G, nodelist=nodelist)

