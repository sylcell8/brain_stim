import os
from isee_engine.bionet.lifcell import LIFCell
from isee_engine.bionet.biocell import BioCell
from isee_engine.bionet.spikestim import SpikeStim
from isee_engine.bionet.ratestim import RateStim
from isee_engine.bionet.morphology import Morphology
from isee_engine.bionet import nrn,bionet_io
import neuron

from neuron import h

pc = h.ParallelContext()    # object to access MPI methods

nhost = int(pc.nhost())



'''
Created on May 20, 2014

@author: sergeyg
'''

class Network(object):
    '''
    Contains methods for instantiating the NEURON network
    '''


    def __init__(self,conf,graph):
        '''
        Constructor
        '''
        bionet_io.print2log0('Setting up network...')

        self.conf = conf

        self.graph = graph



        
    def make_cells(self):   
        '''
        Instantiate cells based on parameters provided in the InternalCell table and Internal CellModel table

        '''

        self.cells = {}

        for gid,node_prop in self.graph.get_internal_nodes():  

            if node_prop['level_of_detail']=='biophysical':
                self.cells[gid] = BioCell(self.conf,node_prop)
            elif node_prop['level_of_detail']=='intfire':
                self.cells[gid] = LIFCell(self.conf,node_prop)
            else:
                bionet_io.print2log0('ERROR: not implemented class');
                raise NotImplementedError('not implemented cell class')
                nrn.quit_execution()
                

        pc.barrier() # wait for all hosts to get to this point

        self.make_morphologies()
        self.set_seg_props()                # set segment properties by creating Morphologies
        self.set_tar_segs()               # set target segments needed for computing the synaptic innervations

        bionet_io.print2log0('Cells are instantiated')


    def make_stims(self):

        self.stims = {}
        
        for k,v in self.conf["run"]["connect_external"].items():
            if v==True:
                self.graph.load_external_nodes(k)
                self.make_input_stims(k)



    def make_input_stims(self,input_name):
        
        '''
        Set stimuli as models of external cells
        '''
        input_conf=self.conf['external'][input_name]
        connections = bionet_io.load_h5(input_conf['connections'])
        indptr = connections['indptr'][...]  # read from file all indptr - has info on which lines to read from hdf5

        input_prop = self.graph.external[input_name]
        src_gids_set = set()
        self.stims[input_name] = {} # createa nested dictionary for a specific input
        
        for tar_gid in self.graph.gids_on_rank["all"]:
            src_gids = connections["src_gids"][indptr[tar_gid]:indptr[tar_gid+1]]
            src_gids_set.update(src_gids)


        for sid,stim_prop in self.graph.get_external_nodes(input_name,gids = src_gids_set):        

#TODO: change to use  stim_prop['level_of_detail'] for consistency with make_cells
            if input_conf["mode"]=="file":  
                self.stims[input_name][sid] = SpikeStim(stim_prop,input_prop)
            if input_conf["mode"]=="random":  
                self.stims[input_name][sid] = RateStim(stim_prop,input_prop)



    def make_morphologies(self):
        '''
        Creating a Morphology object for each biophysical model

        '''
        self.morphologies = {}          # dictionary for objects of Morphology class

        for gid,node_prop in self.graph.get_internal_nodes():  

            if node_prop['level_of_detail']=="biophysical":
                model_id = node_prop['model_id']
                if model_id not in self.morphologies.keys():    # if morphology is not yet created then create
                    hobj = self.cells[gid].hobj                 # get hoc object (hobj) from the first cell with a new morphologys               
                    morph = Morphology(hobj)
                    self.cells[gid].set_morphology(morph)    # associate morphology with a cell   
                    self.morphologies[model_id] = morph      # create a single morphology object for each model_group which share that morphology
                else:
                    morph = self.morphologies[model_id]      # create a single morphology object for each model_group which share that morphology

                    self.cells[gid].set_morphology(morph)    # associate morphology with a cell

        bionet_io.print2log0("Created morphologies")
                    



    def set_seg_props(self):
        '''
        Set morphological properties for biophysically (morphologically) detailed cells

        '''
        
        for model_id, morphology in self.morphologies.items():

            morphology.set_seg_props()

        bionet_io.print2log0("Set segment properties")



                

    def calc_seg_coords(self):
        '''
        Needed for the ECP calculations
        '''

        for model_id, morphology in self.morphologies.items():

#            print "model_id:", model_id, "calc seg_coords"
            morph_seg_coords = morphology.calc_seg_coords()    # needed for ECP calculations

            for gid, cell_prop in self.graph.select_internal_nodes(model_id = model_id):
                self.cells[gid].calc_seg_coords(morph_seg_coords)   

        bionet_io.print2log0("Set segment coordinates")


    def set_tar_segs(self):
        '''
        Find target segments for cells based on target and source connection labels.
        Neeeds con_types file
        '''
        
        for model_id, morphology in self.morphologies.items():

            con_prop_model_df = self.graph.get_con_prop4model(model_id)  # get all possible connnection types for a particuar model_id/morphology
            morphology.find_tar_segs(con_prop_model_df)

        bionet_io.print2log0("Set target segments")
        

    def set_connections(self):

        self.init_connections()        
        bionet_io.print2log0('Setting up connections...')

        for k,v in self.conf["run"]["connect_external"].items():
            if v==True:
                self.set_external_connections(k)
                
        if self.conf["run"]["connect_internal"]==True:
            self.set_internal_connections()    # set connections



    def init_connections(self):

        bionet_io.print2log0('Initializing all connections. Will flush all if exist')
         
        for gid, cell in self.cells.items():
            cell.init_connections()


    def scale_weights(self,factor):

        bionet_io.print2log0('Scaling all connection weights')
         
        for gid, cell in self.cells.items():
            cell.scale_weights(factor)


    def set_external_connections(self,input_name):

        bionet_io.print2log0('Setting connections from  %s' % input_name)

        connections = bionet_io.load_h5(self.conf['external'][input_name]['connections']) # just a file handle
        indptr = connections['indptr'][...]  # read from file all indptr - has info on which lines to read from hdf5

        syn_counter=0

        for tar_gid,tar_cell in self.cells.items():

            src_gids = connections['src_gids'][indptr[tar_gid]:indptr[tar_gid+1]]
            nsyns = connections['nsyns'][indptr[tar_gid]:indptr[tar_gid+1]] # read from hdf5 nsyns and src_gids for a tar_gid
            for src_gid,nsyn in zip(src_gids,nsyns):
                con_params,syn_params = self.graph.get_edge_properties(tar_gid, src_gid, input_name)
                stim = self.stims[input_name][src_gid]
                tar_cell.set_syn_connections(nsyn, syn_params, con_params, src_gid, stim)

                syn_counter+=nsyn
                    
        pc.barrier() # wait for all hosts to get to this point

        bionet_io.print2log0('    set %d synapses' % syn_counter)


    def set_internal_connections(self):
        '''
        Set recurrent connections
        '''

        bionet_io.print2log0('Setting internal connections...')
        
        connections = bionet_io.load_h5(self.conf["internal"]['connections'])
        indptr = connections['indptr'][...]  # read from file all indptr - has info on which lines to read from hdf5

        syn_counter = 0
        for tar_gid,tar_cell in self.cells.items():

            src_gids = connections['src_gids'][indptr[tar_gid]:indptr[tar_gid+1]]
            nsyns = connections['nsyns'][indptr[tar_gid]:indptr[tar_gid+1]] # read from hdf5 nsyns and src_gids for a tar_gid
            
            for src_gid,nsyn in zip(src_gids,nsyns):
                con_params,syn_params = self.graph.get_edge_properties(tar_gid, src_gid)
                tar_cell.set_syn_connections(nsyn, syn_params, con_params, src_gid)
                syn_counter+=nsyn
        bionet_io.print2log0('    set %d synapses' % syn_counter)

     

    def set_ptr2im(self):    # set pointers to i_membrane in each cell 
            
        for gid, cell in self.cells.items():
            cell.set_ptr2im()



    def set_ptr2e_extracellular(self):  #Fahimeh

        for gid, cell in self.cells.items():
            cell.set_ptr2e_extracellular()

        





