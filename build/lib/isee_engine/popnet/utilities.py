
import warnings
import numpy as np
import scipy.interpolate as spinterp
import collections
from isee_engine.nwb import FiringRate
import h5py
import itertools
import scipy.io as sio
import os
import json

def list_of_dicts_to_dict_of_lists(list_of_dicts, default=None):
    
    new_dict = {}
    for curr_dict in list_of_dicts:
        print curr_dict.keys()
    
#     return {key:[item[key] for item in list_of_dicts] for key in list_of_dicts[0].keys()}

class KeyDefaultDict(collections.defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError
        else:
            ret = self[key] = self.default_factory(key)
            return ret

def create_firing_rate_server(t, y):

    warnings.warn('Hard coded bug fix for mindscope council 4/27/15')
    t = t/.001/200
    interpolation_callable = spinterp.interp1d(t, y, bounds_error=False, fill_value=0)
#     print t[-1]
#     print interpolation_callable(1.), interpolation_callable(2.)

    
#     plt.plot(t,y)
# #     plt.show()

     
    return lambda t: interpolation_callable(t)

def create_nwb_server_dict(file_name):

    def cursor_factory(gid):
        
        
        f = h5py.File(file_name, 'r')
        curr_firing_rate = FiringRate.get_acquisition(f,gid)
        y = curr_firing_rate.data[:]
        t = np.arange(len(y))*curr_firing_rate.scales[0].data
        f.close()

        return create_firing_rate_server(t, y)
        
    return KeyDefaultDict(cursor_factory)

def create_nwb_server_file_path(nwb_file_name, nwb_path):
    
    f = h5py.File(nwb_file_name, 'r')
    y = f['%s/data' % nwb_path][:]
    dt = f['%s/data' % nwb_path].dims[0][0].value
    t = np.arange(len(y))*dt
    
    f.close()
    
    return create_firing_rate_server(t, y)

def get_mesoscale_connectivity_dict():

    # Extract data into a dictionary:
    mesoscale_data_dir = '/data/mat/iSee_temp_shared/packages/mesoscale_connectivity'
    nature_data = {}
    for mat, side in itertools.product(['W', 'PValue'],['ipsi', 'contra']):
        data, row_labels, col_labels = [sio.loadmat(os.path.join(mesoscale_data_dir, '%s_%s.mat' % (mat, side)))[key]for key in ['data', 'row_labels', 'col_labels']]
        for _, (row_label, row) in enumerate(zip(row_labels, data)):
            for _, (col_label, val) in enumerate(zip(col_labels, row)):
                nature_data[mat, side, str(row_label.strip()), str(col_label.strip())] = val
    
    return nature_data

def reorder_columns_in_frame(frame, var):
    varlist = [w for w in frame.columns if w not in var]
    return frame[var+varlist]

def population_to_dict_for_dataframe(p):
    
    black_list = ['firing_rate_record', 
                  'initial_firing_rate', 
                  'metadata', 
                  't_record']
    
    json_list = ['p0', 'tau_m']
    
    return_dict = {}
    p_dict = p.to_dict()

    for key, val in p_dict['metadata'].items():
        return_dict[key] = val
    
    for key, val in p_dict.items():
        if key not in black_list:
            if key in json_list:
                val = json.dumps(val)
            return_dict[key] = val
            
    return return_dict

def network_dict_to_target_adjacency_dict(network_dict):
    
    print network_dict
    
if __name__ == "__main__":
    pass
    
# simulation.run()



# # Create configuration file
# Configuration(node_table=node_table_file_name,
#               model_table=model_table_file_name,
#               checkpoint_file_name = checkpoint_file_name,
#               checkpoint_period = checkpoint_period,
#               t0=t0,
#               tf=tf,
#               dt=dt).to_json(save_file_name=configuration_file_name)



# if __name__ == "__main__":
#     
#     # Settings:
#     file_name = '/data/mat/iSee_temp_shared/external_inputs/anton_flash_example/anton_flash_example.nwb'
#     x = create_nwb_cursor_dict(file_name)
#     for ii in range(9000):
#         print ii, x[ii]
    
#     file_name = '/local2/anton_flash_example.nwb'
#     f = h5py.File(file_name, 'r')
#     import time
#     t0 = time.time()
#     for ii in range(9000):
# #         print ii, FiringRate.get_acquisition(f,ii)
#         print ii, f['/acquisition/firing_rate/%s/data' % ii]
# 
#     print time.time() - t0
# 
#     f.close()

# # Initializations:
# gid_list = range(number_of_neurons)
# 
# f = h5py.File(file_name, 'r')
# gid_firing_rate_dict = {}
# for gid in gid_list:
#     
#     curr_firing_rate = FiringRate.get_acquisition(f,gid)
#     
#     firing_rate = curr_firing_rate.data[:]
#     print gid, firing_rate.max()
#     t = np.arange(len(firing_rate))*curr_firing_rate.scales[0].data
#     gid_firing_rate_dict[gid] = (t, firing_rate)
# f.close()
# 
# fig, ax = plt.subplots()
# 
# for gid in gid_list:
#     ax.plot(*gid_firing_rate_dict[gid])
#     
# plt.show()
# 
# 
# if __name__ == "__main__":
#     t = np.array([0,1,2,3])
#     y = np.array([5,8,3,1])
#     c = create_firing_rate_server(t, y)
#     print c(-0.1)

