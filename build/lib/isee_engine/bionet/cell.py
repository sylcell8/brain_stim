from neuron import h
import numpy as np
from isee_engine.bionet import bionet_io,util


pc = h.ParallelContext()    # object to access MPI methods


class Cell(object):
    '''
    Properties and method of a basecell class
    '''

    def __init__(self,cell_prop):
        
        self.gid = cell_prop.name   # the name of the series is the gid
        self.prop = cell_prop  

        x_soma = self.prop['x_soma'] # needed to do those in sequence because Series did not inherite the dtype from DataFrame 
        y_soma = self.prop['y_soma'] # need to look for a more elegant solution to this 
        z_soma = self.prop['z_soma']
        
        self.pos_soma = np.array([x_soma,y_soma,z_soma]).reshape(3,1)

#        self.prng = np.random.RandomState(self.gid) # generate random stream based on gid
#        self.netcons = []   # list of NetCons
#        self.rand_streams = []

        pc.set_gid2node(self.gid, int(pc.id()))         # register the cell:        


    def init_connections(self):

        self.netcons = []
        self.rand_streams = []
        self.prng = np.random.RandomState(self.gid) # generate random stream based on gid

    def scale_weights(self,factor):
        
        for nc in self.netcons:
            weight=nc.weight[0]
            nc.weight[0]=weight*factor 


    def set_syn_connections(self): 

        bionet_io.print2log0('class does not exist')
        raise NotImplementedError


        
    def get_rand_stream(self):
          
        rs = h.Random()
        rs.Random123(self.gid,len(self.rand_streams))
        self.rand_streams.append(rs)
#        rs.negexp(1.0)  # 1 because we want 1 spike per interspike interval on average
        return rs







                
        



