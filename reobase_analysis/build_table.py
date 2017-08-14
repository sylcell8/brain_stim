#import os,sys
import glob
import numpy as np
import reobase_analysis.generate_utils as g
import reobase_analysis.tchelpers as tc
import reobase_analysis.reobase_utils as ru
from isee_engine.bionet.stimxwaveform import stimx_waveform_factory


"""
Script to build h5 files containing organized run info for all runs of a particular amplitude
Will include all electrodes. Has no overwrite protection
"""

### Params ###
#gid = '313862022'
#gid = '314900022'
gid = '320668879'
stim_type = 'dc_lgn_poisson'
#inputs = [-0.01,-0.02,-0.03,-0.04,-0.05]
#inputs = [-0.06,-0.07,-0.08,-0.09,-0.10]
inputs = [-0.09,-0.10]
trial = 0
cell_csv_pattern = '/*_cell.csv'


# Get on with it...
table = ru.build_dc_df()
cell_out_dir = ru.get_reobase_folder('Run_folder/outputs', stim_type, gid)

for amp in inputs:
    print 'Build table for amp = {}...'.format(amp)

    amp_output = ru.concat_path(cell_out_dir, ru.get_dc_dir_name(9999,amp,trial)).replace('9999', '*')

    for out_folder in glob.iglob(amp_output):
        out_dir = out_folder.split('/')[-1]
        el = int([x for x in out_dir.split('_') if x.startswith('el')][0][2:]) # parse el from folder name..
        config_path = ru.get_config_resolved_path(out_folder, el, amp)
        conf = tc.get_json_from_file(config_path)
            
        el_conf = conf["extracellular_stimelectrode"]
        electrodes_dir = conf['output']['electrodes_dir']
        electrodes_dir = ru.get_dir_root() + '/' + '/'.join(electrodes_dir.split('/')[2:])

        waveform = stimx_waveform_factory(conf)
        amp = waveform.amp
        spikes = ru.get_spikes_data(out_folder)
        el_xyz = ru.get_electrode_xyz(ru.get_electrode_path(electrodes_dir, gid, el)).flatten()
        cell_xyz = ru.get_cell_xyz(glob.glob(out_folder + cell_csv_pattern)[0]).flatten()
        el_dist = np.linalg.norm(el_xyz - cell_xyz)
        run_id = ru.resolve_run_id(gid, el, amp)
    
    
        table.loc[run_id] = [trial, el, el_xyz[0], el_xyz[1], el_xyz[2], el_dist, amp, spikes]

    print 'Data collected. Writing h5...'
    fpath = ru.get_reobase_folder('Run_folder/result_tables', stim_type, ru.get_table_filename(gid, amp))
    ru.write_table_h5(fpath, table)
    print 'Done.'








