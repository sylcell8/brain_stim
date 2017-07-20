#import os,sys
import numpy as np
import itertools
#import random

import script.generate_utils as g
import script.tchelpers as tc
import reobase_utils as ru
from isee_engine.bionet.stimxwaveform import stimx_waveform_factory


gid = '313862022'
out_dir = '/Volumes/aibs/mat/Fahimehb/Data_cube/reobase/Run_folder/outputs/dc/' ## TODO source from conf file
cell_out_dir = out_dir + gid + '/'

els = range(100)
#els = random.sample(range(1020), 500)
inputs = [-0.03]
trial = 0 # TODO hook this up!

#%% Build table
print 'Build table...'

table = ru.build_dc_df()
runs = itertools.product(els, inputs)

for run in runs: # (el, i_stim) pairs
    electrode = run[0] # safe to use el from here b/c folder was built from this
    rf = g.dc_folder_format(g.get_dc_key(*run), trial) + '/'
    out_folder = cell_out_dir + rf
    config_path = ru.get_config_resolved_path(out_folder, electrode)

    try:
        conf = tc.get_json_from_file(config_path)
    except:
        print 'unable to find config at ' + config_path
        continue;
        
    el_conf = conf["extracellular_stimelectrode"]
    electrodes_dir = conf['output']['electrodes_dir']
    # TODO if on mac...
    electrodes_dir = '/Volumes/'+'/'.join(electrodes_dir.split('/')[2:])

    waveform = stimx_waveform_factory(conf)
    amp = waveform.amp
    spikes = ru.get_spikes_data(out_folder)
    el_xyz = ru.get_electrode_xyz(ru.get_electrode_path(electrodes_dir, gid, electrode)).flatten()
    cell_xyz = ru.get_cell_xyz(out_folder + '1_cells.csv').flatten() # TODO this is fragile
    el_dist = np.linalg.norm(el_xyz - cell_xyz)
    run_id = ru.resolve_run_id(gid, electrode, amp)

    table.loc[run_id] = [trial, electrode, el_xyz[0], el_xyz[1], el_xyz[2], el_dist, amp, spikes]

print 'Table created'


#%% Write out to h5

#fpath = '/Users/Taylor/projects/allen2017/table.h5'
fpath = '/Volumes/aibs/mat/Taylorc/test_table.h5'
ru.write_table_h5(fpath, table)



