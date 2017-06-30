from isee_engine.bionet import bionet_io,util
from neuron import h

'''
Created on Aug 22, 2016

@author: sergeyg
'''

class Stim(object):
    '''
    classdocs
    '''


    def __init__(self, stim_prop):
        '''
        Constructor
        '''

        self.stim_gid = stim_prop.name
        self.rand_streams = []


    def set_stim(self): 
        '''
        This method is implemented in the child class
        '''

        bionet_io.print2log0('class does not exist')
        raise NotImplementedError


    def get_rand_stream(self):
          
        rs = h.Random()
        rs.Random123(self.stim_gid,len(self.rand_streams))
        self.rand_streams.append(rs)
        return rs
        