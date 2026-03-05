from isee_engine.bionet import nrn,bionet_io

from neuron import h



def exp2syn(nsyn, syn_params, secs, secs_x):
    '''
    Create exp2syn synapses
    
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
    syns = [];        

    if syn_params['level_of_detail']=='exp2syn':
        erev = syn_params['erev']           # ideally we would get properties of individual synapse models from a synaptic model file
        tau1 = syn_params['tau1'] 
        tau2 = syn_params['tau2'] 

        for x,sec in zip(secs_x,secs):
            syn = h.Exp2Syn(x,sec=sec)
            syn.e = erev
            syn.tau1 = tau1
            syn.tau2 = tau2
            syns.append(syn) 

    else:
        bionet_io.print2log0('ERROR: not implemented synaptic model')
        raise NotImplementedError('not implemented synaptic model')
        nrn.quit_execution()

    

    return syns


