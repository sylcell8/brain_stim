import json
from isee_engine.bionet.cell import Cell
from isee_engine.bionet import bionet_io,nrn

from neuron import h
pc = h.ParallelContext()    # object to access MPI methods

class LIFCell(Cell):
    '''
    Properties and method of cells
    '''

    def __init__(self,conf,cell_prop):
        
        Cell.__init__(self,cell_prop)
        self.set_params(cell_prop['electrophysiology'])

        self.set_spike_detector()


        
    def set_spike_detector(self):
        
        nc = h.NetCon(self.hobj, None)
        pc.cell(self.gid, nc)

    
    def set_params(self,params_file):
    
    
        with open(params_file) as params_file:
            params = json.load(params_file)
        params_file.close()
    
        # Need to make sure that it is OK to create hobj only under certain circumstances; alternatively, we need to create a dummy hobj.
        if params['type'] == 'NEURON_IntFire1':
            self.hobj = h.IntFire1()
            self.hobj.tau = params['tau'] * 1000.0 # Convert from seconds to ms.
            self.hobj.refrac = params['refrac'] * 1000.0 # Convert from seconds to ms.
    
        else:
            bionet_io.print2log0('ERROR: Point neuron type %s is not currently supported by the converter to NEURON simulator; exiting.' % (params['type']))
            nrn.quit_execution()
    

    def set_ptr2im(self): 
        
        pass



    def set_syn_connections(self, nsyn, syn_params, con_prop, src_gid, stim=None):

        '''
        Set synaptic connection
        '''

        
        if syn_params['level_of_detail']=='instanteneous':

            sign = syn_params['sign']
    
            if stim:
                nc = h.NetCon(stim.hobj, self.hobj)
            else:
                nc = pc.gid_connect(src_gid, self.hobj)

            weight = nsyn*syn_params['weight']    # scale weight by the number of synapse the artificial cell receives

#            weight = nsyn*con_prop['weight']    # scale weight by the number of synapse the artificial cell receives
            delay = con_prop['delay']
    
            nc.weight[0] = sign*weight; 
            nc.delay = delay      
            self.netcons.append(nc)


        else:
            bionet_io.print2log0('ERROR: not implemented synaptic model')
            raise NotImplementedError('not implemented synaptic model')
            nrn.quit_execution()




                
        



