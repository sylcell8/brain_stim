# analyze single cell reobase data
# analysis is per cell, many electrodes

#import os,sys
import pandas as pd
import numpy as np
import h5py as h5
import itertools
import random


import script.generate_utils as g
import script.tchelpers as tc
from reobase_utils import *

from isee_engine.bionet.stimxwaveform import stimx_waveform_factory


gid = '313862022'
out_dir = '/Volumes/aibs/mat/Fahimehb/Data_cube/reobase/Run_folder/outputs/dc/' ## TODO source from conf file
cell_out_dir = out_dir + gid + '/'

els = range(100)
#els = random.sample(range(1020), 500)
inputs = [-0.03]
trial = 0 # TODO hook this up!

# grab data via functions so code is more agnostic to order of analysis,
# also b/c reading files and resolving folder names is likely to be used elsewhere -- thus are utils
def get_spikes_data(out_path):
    cellvars = tc.get_cv_files(out_path, cells=[0])[0]
    return cellvars['spikes'].value
    
def get_electrode_xyz(electrode_pos_path): # Ideally you would use the method bionet uses
    # mesh files are unnecessary for this study
    electrode_pos_df = pd.read_csv(electrode_pos_path, sep=' ')
    return electrode_pos_df.as_matrix(columns=['pos_x', 'pos_y', 'pos_z'])
    
def get_cell_xyz(cell_file): # Ideally you would use the method bionet uses
    cell_props_df = pd.read_csv(cell_file, sep=' ')
    return cell_props_df.as_matrix(columns=['x_soma', 'y_soma', 'z_soma'])

def resolve_run_id(gid, electrode, i):
    stringified = map(str, [ gid, electrode, '{0:.0f}'.format(np.abs(i*1000)) ])
    return '_'.join(stringified) # using current in micro amps  

def get_electrode_path(electrodes_dir, gid, el):
    return '/'.join( [electrodes_dir, gid + '_' + g.fill_el(el) + '.csv'] )

def get_config_resolved_path(out_folder, el):
    return out_folder + 'config_el' + g.fill_el(el) + '_resolved.json'

#%%

# Setup Dataframe
table = build_dc_df()

runs = itertools.product(els, inputs)
print 'Build table'

for run in runs: # (el, i_stim) pairs
    rf = g.dc_folder_format(g.get_dc_key(*run), trial) + '/'
    out_folder = cell_out_dir + rf
    
    
#    if ~os.path.isdir(out_folder): # Will fail regardless if you do not have w permissions for that dir
#        print 'no folder found for {} -- {}'.format(run, out_folder)
#        continue
#    else:
#        print 'folder found for {}'.format(run)

    try:
        electrode = run[0] # safe to use el from here b/c folder was built from this
        config_path = get_config_resolved_path(out_folder, electrode)
        conf = tc.get_json_from_file(config_path)
    except:
        continue;
        
    el_conf = conf["extracellular_stimelectrode"]
    electrodes_dir = conf['output']['electrodes_dir']
    # TODO if on mac...
    electrodes_dir = '/Volumes/'+'/'.join(electrodes_dir.split('/')[2:])

    waveform = stimx_waveform_factory(conf)
    amp = waveform.amp
    spikes = get_spikes_data(out_folder)
    el_xyz = get_electrode_xyz(get_electrode_path(electrodes_dir, gid, electrode)).flatten()
    cell_xyz = get_cell_xyz(out_folder + '1_cells.csv').flatten() # TODO this is fragile
    el_dist = np.linalg.norm(el_xyz - cell_xyz)
    run_id = resolve_run_id(gid, electrode, amp)

    table.loc[run_id] = [trial, electrode, el_xyz[0], el_xyz[1], el_xyz[2], el_dist, amp, spikes]

print 'Table created'


#%% Write out to h5

#fpath = '/Users/Taylor/projects/allen2017/table.h5'
fpath = '/Volumes/aibs/mat/Taylorc/test_table.h5'
write_table_h5(fpath, table)



