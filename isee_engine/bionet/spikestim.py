from isee_engine.bionet.stim import Stim
from neuron import h

'''
Created on Aug 22, 2016

@author: sergeyg
'''

class SpikeStim(Stim):
    '''
    Implements external input as a spike times
    '''


    def __init__(self, stim_prop,input_prop):
        '''
        Parameters
        ----------
        stim_prop:    pandas Series
            Includes properties of individual external cells
        input_prop:    dictionary
            Includes properties of the external input as well as parameters of external input.
        
        
        Returns
        -------
            
            
        '''
        Stim.__init__(self,stim_prop)

        self.set_stim(stim_prop,input_prop)
        
    def set_stim(self,stim_prop,input_prop):

        spike_trains_handle = input_prop["spike_trains_handle"]
        self.spike_train = spike_trains_handle['%d/data' %self.stim_gid][:]

        self.train_vec = h.Vector(self.spike_train)
        vecstim = h.VecStim(); 
        vecstim.play(self.train_vec)
        
        self.hobj = vecstim
        