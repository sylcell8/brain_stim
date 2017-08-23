import isee_engine.nwb as nwb
import poisson
# import h5py
import numpy as np

"""
Write nwb file with poisson spike train
"""

def build_spike_trains(firing_rate, T, num_trials, num_cells):
    """
    :param firing_rate:
    :param T: listed unit is millisecond
    :param num_trials: each trial is independent
    :param num_cells: use a given number of input cells
    :return:
    """

    input_spike_file_name = '/Users/Taylor/projects/allen2017/poisson_input_spk_train.nwb'
    f = nwb.create_blank_file(input_spike_file_name, force=True)

    for i in range(num_trials):
        for c in range(num_cells):
            train = np.array(poisson.homogeneous_list(firing_rate,T))
            nwb.SpikeTrain(train, unit='millisecond').add_to_processing(f, 'trial_%s' % i)

    f.close()


# build_spike_trains(5, 3, 2, 6)