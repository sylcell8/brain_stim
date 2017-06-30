import h5py
import numpy as np 
from isee_engine import nwb

file_name = 'example.nwb'
file_name_2 = 'example_2.nwb'

'''
Example 1: Storing spike times from a single neuron:
'''
f = nwb.create_blank_file(file_name, force=True)
data = nwb.SpikeTrain(np.array([.1,.5,1.19]), unit='second')
data.add_to_stimulus(f)
f.close()

f = h5py.File(file_name, 'r')
spike_train = nwb.SpikeTrain.get_stimulus(f, 0)
y_values_new = spike_train.data[:] # Collects data from file
print y_values_new
f.close()

f = h5py.File(file_name, 'r')
spike_train = nwb.SpikeTrain.get_stimulus(f, 0)
y_values_new = spike_train.data # File handle into the data
print y_values_new
f.close()
print



'''
Example 2: Storing spike times from a two neurons, separate data sets:
'''
f = nwb.create_blank_file(file_name, force=True)
nwb.SpikeTrain(np.array([.1,.5,1.19]), unit='second').add_to_processing(f,'example_1')
nwb.SpikeTrain(np.array([.2,.6,1.29]), unit='second').add_to_processing(f,'example_1')
f.close()

f = h5py.File(file_name, 'r')
spike_train = nwb.SpikeTrain.get_processing(f, 'example_1')
print spike_train[0].data[:], spike_train[1].data[:]
f.close()
print

<<<<<<< HEAD

=======
sys.exit()
>>>>>>> e1b0ffd7248e02279411b99ef80de286c5f10fc0

'''
Example 3: Storing spike times from a two neurons, combined data set:
'''
f = nwb.create_blank_file(file_name, force=True)
spike_times = np.array([.1,.5,1.19])
neuron_index = np.array([0,2,3])
scale = nwb.Scale(spike_times, 'time', 'second')
nwb.SpikeTrain(neuron_index, scale=scale, metadata={'number_of_neurons':5}).add_to_stimulus(f)
f.close()

f = h5py.File(file_name, 'r')
spike_train = nwb.SpikeTrain.get_stimulus(f, 0)
print spike_train.metadata['number_of_neurons']
print spike_train.data[:]
print spike_train.scales[0].data[:]
f.close()
print

sys.exit()

'''
Example 4: Store 3 firing rate traces as acquisition
They share a t-axis, and each have their own metadata
'''
f = nwb.create_blank_file(file_name, force=True)
scale = nwb.Scale(np.arange(5), 'time', 'second')
nwb.FiringRate(1*np.ones(5), scale=scale, metadata={'name':'eeny'}).add_to_acquisition(f)
nwb.FiringRate(2*np.ones(5), scale=scale, metadata={'name':'meeny'}).add_to_acquisition(f)
nwb.FiringRate(3*np.ones(5), scale=scale, metadata={'name':'miny'}).add_to_acquisition(f)
nwb.FiringRate(4*np.ones(5), scale=scale, metadata={'name':'moe'}).add_to_acquisition(f)
f.close()

f = h5py.File(file_name, 'r')
for data in nwb.FiringRate.get_acquisition(f):
    print data.metadata['name'], data.scales[0].data[:], data.data[:] 
f.close()
print

'''
Example 5: Store voltage traces with sampling rate scale:
'''
f = nwb.create_blank_file(file_name, force=True)
scale = nwb.DtScale(.1, 'time', 'second')
nwb.TimeSeries(np.array([.1,.2,.1]), scale=scale, dimension='voltage', unit='volt').add_to_acquisition(f)
f.close()

f = h5py.File(file_name, 'r')
data = nwb.TimeSeries.get_acquisition(f, 0)
print data.scales[0].dt, data.scales[0].unit, data.data[:] 
f.close()
print

'''
Example 6: Storing a grayscale movie: Time can go on any axis
'''
t_values = np.arange(20)*.1
row_values = np.arange(5)
col_values = np.arange(10)
data_values = np.empty((20,5,10)) # Junk movie data

f = nwb.create_blank_file(file_name, force=True)
t_scale = nwb.Scale(t_values, 'time', 'second')
row_scale = nwb.Scale(row_values, 'distance', 'pixel')
col_scale = nwb.Scale(col_values, 'distance', 'pixel')

data = nwb.GrayScaleMovie(data_values, scale=(t_scale, row_scale, col_scale))
data.add_to_stimulus(f)
    
data_handle = nwb.GrayScaleMovie.get_stimulus(f).data
print data_handle[:].shape

'''
Example 7: Linking to external file:
'''
f = nwb.create_blank_file(file_name, force=True)
scale = nwb.Scale(np.zeros(10), 'time', 'second')
nwb.TimeSeries(np.ones(10), scale=scale, dimension='voltage', unit='volt', metadata={'foo':1}).add_to_acquisition(f)
temp_file_name = f.filename
f.close()

f = h5py.File(file_name, 'r')
f2 = nwb.create_blank_file(file_name_2, force=True)
data = nwb.TimeSeries.get_acquisition(f, 0) # Grab from one file
data.add_to_stimulus(f2) # Add to the other
f.close()
f2.close()

f = h5py.File(file_name_2)
data = nwb.TimeSeries.get_stimulus(f, 0)
print data.data.file.filename # Does not equal temp_file_name_2, because it is a link
f.close()
