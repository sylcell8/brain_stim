import pandas as pd
from isee_engine.bionet import bionet_io
from neuron import h
import imp

pc = h.ParallelContext()    # object to access MPI methods


'''
Created on Jul 5, 2016

@author: sergeyg
'''

class Graph(object):
    '''
    classdocs
    '''


    def __init__(self,conf):
        '''
        Constructor
        '''

        self.internal = {} # dictionary for internal nodes 
        self.external = {}  # dictionary for external nodes

        self.conf = conf
        self.load_internal_nodes()        # load internal nodes 
        self.set_gid_groups()
        self.load_edge_props()            # load properties of the edges


        self.weightfuncs = imp.load_source('weightfuncs', conf["setup"]["weight_funcs"])


            
    def get_spike_train(self,src_gid):

        spike_trains = self.external['spike_trains']
        spike_train  = spike_trains['%d/data' %src_gid][:]

        return spike_train
     



    def get_edge_properties(self,tar_gid,src_gid,input_name=None):

        if input_name==None:
            src_prop = self.internal['all_nodes'].loc[src_gid] # get source label
        else:
            src_prop = self.external[input_name]['all_nodes'].loc[src_gid] # get source label
            
        tar_prop = self.internal['all_nodes'].loc[tar_gid] # get source label

        edge = (tar_prop["con_type_label"],src_prop["con_type_label"])

        ct_df = self.edge_props['con_types']
        con_prop = ct_df.loc[edge]    # returns a series object
        syn_params = self.edge_props['syn_params'][con_prop.name]

        weight_function = getattr(self.weightfuncs, con_prop['weight_func'])
        weight = weight_function(tar_prop,src_prop,con_prop) # tar_prop and src_prop only include properties from the ref_label
        syn_params["weight"] = weight   # add weight to syn_params
        
        return con_prop, syn_params




    
    def get_internal_nodes(self):
        
        nodes_df = self.internal['rank_nodes']

        return nodes_df.iterrows()


    def get_external_nodes(self,input_name,gids = None):
        

        nodes_df = self.external[input_name]['all_nodes']

        if gids == None: gids = nodes_df.index.values

        return nodes_df.loc[gids].iterrows()




    def select_internal_nodes(self,model_id):
        '''
            Currently use only model_id to do selection
            TODO: make it a more general selector
        '''
        
        nodes_df = self.internal['rank_nodes']

        mask = (nodes_df['model_id']==model_id) # find cell indexes for a given model_id

        select_df = nodes_df[mask]

        return select_df.iterrows()


    def get_con_prop4model(self, model_id):

        '''
        Parameters:
        ----------
        model_id: int
            id of a cell model
            
        Retruns:
        -------
        ctm_df: pd.DataFrame
            rows from the con_types table in which target cells use this model_id
        '''
        nodes_df = self.internal['rank_nodes']

        ct_df  = self.edge_props['con_types']
        
        # get a set of connection labels for a given model. It could be more than one when a model is used in more than one populations
        mask_model_id = (nodes_df['model_id']==model_id)
        model_con_labels = set(nodes_df[mask_model_id]['con_type_label'].values)

        # get rows from the con_types table which include these labels in the target_label column
        mask_tar_con_labels = ct_df.index.get_level_values('target_label').isin(model_con_labels)
        ctm_df = ct_df[mask_tar_con_labels]
        
        return ctm_df

    


    def load_internal_nodes(self):
        
        ''' 
        Load Cell_Table and Cell_Models_Table from the csv files
        
        '''
    
    
        cells_df = bionet_io.load_csv(self.conf["internal"]["cells"])
        cells_df.set_index('id',inplace=True)
        
        cell_models_df = bionet_io.load_csv(self.conf["internal"]["cell_models"])
        cell_models_df.set_index('model_id',inplace=True)
    
        self.set_internal_node_props(cells_df,cell_models_df)

        
    def set_internal_node_props(self,cells_df,cell_models_df):


        rank = int(pc.id());    nhost = int(pc.nhost())
        ncells = len(cells_df.index) # total number of simulated cells
    
    #   Use round-robin to find rows in the dataframe belonging to a particular rank.
    #   We use rows instead of gids because this way we do not depend on integer and incremental gids. Rows start with 0.
    
        rows_rank = range(rank, ncells, nhost) 
        bionet_io.print2log0('Number of ranks: %s' % nhost)
        
        nodes_df = pd.merge(left=cells_df,
                            right=cell_models_df, # connection labels of all cells in the network, not just those on the rank
                            how='left', 
                            left_on='model_id', 
                            right_index=True) # use 'model_id' key to merge

        ref_labels = self.conf["internal"]["ref_labels"]
        nodes_df.rename(columns=ref_labels, inplace=True)   # rename to be able to acces these properties

        self.internal['all_nodes'] = nodes_df[ref_labels.values()]              # node properties of all cells
        
        # keep only nodes which belong to this rank 
        rank_nodes_df = nodes_df.iloc[rows_rank]

        self.internal['rank_nodes'] = rank_nodes_df # include rows only for cells belonging to a particular rank
        self.internal['cell_models'] = cell_models_df 

        for ind,val in rank_nodes_df.iterrows():

            if val["level_of_detail"]=="biophysical":
                ephys_file_name = self.conf["internal"]["bio_ephys_dir"]+'/'+val["electrophysiology"]
                rank_nodes_df.set_value(ind,"electrophysiology",ephys_file_name)

                morph_file_name = self.conf["internal"]["bio_morph_dir"]+'/'+val["morphology"]
                rank_nodes_df.set_value(ind,"morphology",morph_file_name)

            if val["level_of_detail"]=="intfire":
                ephys_file_name = self.conf["internal"]["lif_ephys_dir"]+'/'+val["electrophysiology"]
                rank_nodes_df.set_value(ind,"electrophysiology",ephys_file_name)
    

        bionet_io.print2log0('Set up node properties ')



    
    def set_gid_groups(self):
    
    
        gid_groups = self.conf["groups"]
        self.gids_on_rank = {}   # all gids on this rank

        gids_rank_all = self.internal['rank_nodes'].index
        self.gids_on_rank["all"] = gids_rank_all
        
        nodes_on_rank_df = self.internal['rank_nodes']

        bio_gids =  nodes_on_rank_df[nodes_on_rank_df["level_of_detail"]=='biophysical'].index

        self.gids_on_rank["biophysical"] = bio_gids   # all gids on this rank
    
        for group_name, group_gids in gid_groups.items():
    
            self.gids_on_rank[group_name] = list(set(gids_rank_all) & set(group_gids))    # alternative implementation





    def load_edge_props(self):


        self.edge_props = {}

        con_types_df = bionet_io.load_csv(self.conf["internal"]["con_types"])
        con_types_df.set_index(['target_label','source_label'],inplace=True)    # will use MultiIndex
        
        self.edge_props['con_types'] = con_types_df

        self.edge_props['syn_params'] = {}    
        for con_key,con_prop in con_types_df.iterrows():
            params_file = self.conf["manifest"]["$SYN_MODELS_DIR"]+'/'+con_prop['params_file']
            self.edge_props['syn_params'][con_key] = bionet_io.load_json(params_file)
        
    

    def load_external_nodes(self,input_name):
    
        input_prop=self.conf['external'][input_name]
    
        cells_df = bionet_io.load_csv(input_prop["cells"])
        cells_df.set_index('id',inplace=True)
    
        cell_models_df = bionet_io.load_csv(input_prop["cell_models"])
        cell_models_df.set_index('model_id',inplace=True)

        self.set_external_node_props(cells_df,cell_models_df,input_name)
        


    def set_external_node_props(self,cells_df,cell_models_df,input_name):


        input_prop=self.conf['external'][input_name]

        self.external[input_name] = {}

        nodes_df = pd.merge(left=cells_df,
                            right=cell_models_df, # connection labels of all cells in the network, not just those on the rank
                            how='left', 
                            left_on='model_id', 
                            right_index=True) # use 'model_id' key to merge


        ref_labels = input_prop["ref_labels"]
        nodes_df.rename(columns=ref_labels, inplace=True)   # rename to be able to acces these properties
        self.external[input_name]['all_nodes'] = nodes_df


        if input_prop["mode"]=="file":
            self.external[input_name]['spike_trains_handle'] = bionet_io.get_spike_trains_handle(input_prop["spike_trains"], input_prop["trial"])

        if input_prop["mode"]=="random":

            self.external[input_name]['net_stims_params'] = {}
            for model_id, cell_model in cell_models_df.iterrows():
                params_file = input_prop["net_stims_dir"]+'/'+cell_model['electrophysiology']
                self.external[input_name]['net_stims_params'][model_id] = bionet_io.load_json(params_file)   # loaded parameters of nestim

        bionet_io.print2log0('Loaded nodes for %s' % input_name)


    
    