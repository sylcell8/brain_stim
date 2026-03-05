from isee_engine.bionet.stim import Stim
from neuron import h


'''
Created on Aug 22, 2016

@author: sergeyg
'''

class RateStim(Stim):
    '''
    Implements external input as firing rate, which is then used to sample spike times 
    from Poisson's distribution
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
        '''

        Parameters
        ----------
        net_stim_params:    dict
            parameters of net_stim
        rs:    h.Random()
            random stream
        
        '''

        model_id = stim_prop["model_id"]
        net_stim_params = input_prop["net_stims_params"][model_id]


        firing_rate = net_stim_params['firing_rate']
        noise = net_stim_params['noise']
        start = net_stim_params['start']

        rs = self.get_rand_stream() 
        rs.negexp(1.0)

        netstim = h.NetStim(0.5)
        netstim.noiseFromRandom(rs)
        ISI = 1.0/firing_rate;               
        netstim.interval = ISI*1E+3        # mean ISI (ms)
        number_of_spikes = int(10*prm.conf['run']['tstop']/ISI)
        
        netstim.number = number_of_spikes 
        netstim.noise = noise; 
        netstim.start = start

        self.hobj = netstim



        
            