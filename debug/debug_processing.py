import h5py
import numpy as np 
from isee_engine import nwb

file_name = 'debug.nwb'

'''
Example 2: Storing spike times from a two neurons, separate data sets:
'''
f = nwb.create_blank_file(file_name, force=True)
nwb.SpikeTrain(np.array([.1,.5,1.19]), unit='second').add_to_processing(f,'debug')
nwb.SpikeTrain(np.array([.2,.6,1.29]), unit='second').add_to_processing(f, 'debug')
f.close()

f = h5py.File(file_name, 'r')
spike_train = nwb.SpikeTrain.get_processing(f, 'debug')
print spike_train
print spike_train[0].data[:]
f.close()