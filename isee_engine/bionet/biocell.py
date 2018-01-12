import numpy as np
from isee_engine.bionet import util,bionet_io,nrn
import isee_engine.bionet.biophysical as bio
import isee_engine.bionet.synaptic as snp
from isee_engine.bionet.cell import Cell

from neuron import h

pc = h.ParallelContext()    # object to access MPI methods


class BioCell(Cell):
    '''
    Properties and method of cells
    '''

    def __init__(self,conf,cell_prop):


        Cell.__init__(self,cell_prop)

        self.hobj = h.Biophysical()  # create a blank hoc object from template.

        bio.set_morphology(self.hobj,cell_prop['morphology']);

        if cell_prop['fixaxon'] == 'perisomatic':
            bionet_io.print2log0("Fixing axon like perisomatic ")
            bio.fix_axon_perisomatic(self.hobj)

        if cell_prop['fixaxon'] == 'all_active':
            bionet_io.print2log0("Fixing axon like all_active ")
            bio.fix_axon_all_active(self.hobj)

        bio.set_params(self.hobj, cell_prop['electrophysiology'])

        self.set_nseg(conf["run"]["dL"])
#        self.synapses = []
#        self.syn_src_gid = []
#        self.syn_seg_ix = []
        
        self.set_spike_detector(conf["run"]["spike_threshold"])
        self.set_sec_array()

        if conf["run"]["calc_ecp"]:
            self.ptr2im = h.PtrVector(self.nseg)  # pointer vector
            self.ptr2im.ptr_update_callback(self.set_ptr2im)
            self.imVec = h.Vector(self.nseg)          # place here values from pointer to i_membrane

        if conf["run"]["extra_stim"]: #Fahimeh
            self.ptr2e_extracellular = h.PtrVector(self.nseg)
            self.ptr2e_extracellular.ptr_update_callback(self.set_ptr2e_extracellular)

    def set_spike_detector(self,spike_threshold): 
        
        nc = h.NetCon(self.hobj.soma[0](0.5)._ref_v,None,sec=self.hobj.soma[0]);
        nc.threshold = spike_threshold     # attach spike detector to cell
        pc.cell(self.gid, nc)               # associate gid with spike detector

        
    
    def set_nseg(self,dL):    
        '''
        Define number of segments in a cell
        
        '''
        nseg = 0
        for sec in self.hobj.all:
            sec.nseg = 1 + 2 * int(sec.L/(2*dL))
            nseg += sec.nseg # get the total # of segments in the cell

        self.nseg = nseg


    def calc_seg_coords(self,morph_seg_coords):

        '''
        Calculate segment coordinates for individual cells
       
        '''

        phi_y = self.prop['rotation_angle_yaxis']
        phi_z = self.prop['rotation_angle_zaxis']

        RotY = util.rotation_matrix([0,1,0],phi_y)  # rotate segments around yaxis normal to pia
        RotZ = util.rotation_matrix([0,0,1],-phi_z) # rotate segments around zaxis to get a proper orientation
        RotYZ = RotY.dot(RotZ)

    
        self.seg_coords = {}
        self.seg_coords['p0'] = self.pos_soma + np.dot(RotYZ,morph_seg_coords['p0'])  # rotated coordinates around z axis first then shift relative to the soma
        self.seg_coords['p1'] = self.pos_soma + np.dot(RotYZ,morph_seg_coords['p1'])
        self.seg_coords['p05'] = self.pos_soma + np.dot(RotYZ, morph_seg_coords['p05'])


    def set_morphology(self,morph):

        self.morph = morph 



    def set_sec_array(self):

        '''
        Arrange sections in an array to be access by index
        
        self.secs: ndarray of h.Sections
        '''

        secs = []    # build ref to sections
        for sec in self.hobj.all:
            for seg in sec: 
                secs.append(sec)                 # section to which segments belongs

        self.secs = np.array(secs)



    def set_syn_connections(self, nsyn, syn_params, con_prop, src_gid, stim=None):

        '''
        Set synaptic connections
        '''


        tar_segs = self.morph.innerv[con_prop.name]                     # segments which could be targeted

        segs_ix = self.prng.choice(tar_segs['ix'], nsyn, p = tar_segs['p']) # choose nsyn elements from seg_ix with probability proportional to segment area
        con_secs = self.secs[segs_ix]                               # sections where synapases connect
        con_segs_x = self.morph.seg_prop['x'][segs_ix]          # distance along the section where synapse connects, i.e., seg_x

        syns = self.create_synapses(nsyn, syn_params, con_secs, con_segs_x)        
            
        weight = syn_params['weight']
        delay = con_prop['delay']
        self.synapses.extend(syns)
        
#        print "weight:", weight
        self.syn_seg_ix.extend(segs_ix)
        self.syn_src_gid.extend([src_gid]*len(syns))

        for syn in syns:    # connect synapses            
            if stim:
                nc = h.NetCon(stim.hobj, syn)   # stim.hobj - source, syn - target
            else:
                nc = pc.gid_connect(src_gid,syn)
 
            nc.weight[0] = weight; 
            nc.delay = delay      
            self.netcons.append(nc)
            

    def init_connections(self):

        Cell.init_connections(self)

        self.synapses = []
        self.syn_src_gid = []
        self.syn_seg_ix = []

        

    def create_synapses(self, nsyn, syn_params, secs, secs_x):
        '''
        Create synapses given the synaptic model
        
        Parameters
        ----------
        syn_params: dict
            parameters of a synapse
        seg_ix: np.array 
            indexes of segments targeted by synapses
            
        
        Returns
        -------
        syns: list of hoc synapse objects

        '''

        if syn_params['level_of_detail']=='exp2syn':
            syns = snp.exp2syn(nsyn, syn_params, secs, secs_x)

        else:
            bionet_io.print2log0('ERROR: not implemented synaptic model')
            raise NotImplementedError('not implemented synaptic model')
            nrn.quit_execution()

        

        return syns


    
    

    def set_ptr2im(self): 
        
        jseg = 0
        for sec in self.hobj.all:
            for seg in sec:
                self.ptr2im.pset(jseg,seg._ref_i_membrane_) # notice the underscore at the end
                jseg +=1




    def get_im(self): # get membrane currents from PtrVector into imVec (no loop)
        '''
        Get membrane currents from PtrVector into imVec (does not need a loop!)
        
        Returns
        -------
        
        imVec: ndarray
            convert h.Vector to numpy array
        
        '''

        self.ptr2im.gather(self.imVec)       
        

        return self.imVec.as_numpy() #    (nA)


        
    def set_ptr2e_extracellular(self):

        jseg = 0
        for sec in self.hobj.all:
            for seg in sec:
                self.ptr2e_extracellular.pset(jseg, seg._ref_e_extracellular)
                jseg += 1


    def set_e_extracellular(self, vext):

        self.ptr2e_extracellular.scatter(vext)

