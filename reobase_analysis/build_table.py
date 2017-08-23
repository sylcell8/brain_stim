#import os,sys
import glob
import numpy as np
import pandas as pd
import itertools
import reobase_analysis.reobase_utils as ru
from reobase_analysis.analysis import StimType
from isee_engine.bionet.stimxwaveform import stimx_waveform_factory

#import cProfile, pstats, io
#pr = cProfile.Profile()
#pr.enable()

"""
Script to build h5 files containing organized run info for all runs of a particular amplitude
Will include all electrodes. Has no overwrite protection.

Will attempt to include vm information if the stim type is DC. This is only done for DC because it only makes sense for 
a constant input without external input. This allows us to look at the subthreshold response.
If the cell is active (> 1 spikes) then the post-stim vm value is NaN
"""

### Params ###
default_gid = [313862022, 314900022, 320668879][0]
default_inputs = [-0.01,-0.02,-0.03,-0.04,-0.05,-0.06,-0.07,-0.08,-0.09,-0.10]
default_stim_type = StimType.DC_LGN_POISSON


def build(cell_gid, inputs, stim_type, trial=0):
    cell_csv_pattern = '/*_cel[ls]*csv' # ridiculous pattern matching for old files called 1_cell.csv vs new ones called [gid].csv
    cell_out_dir = ru.get_reobase_folder('Run_folder/outputs', stim_type, cell_gid)
    include_delta_vm = stim_type == StimType.DC.value

    for amp in inputs:

        print 'Build data table for amp = {}...'.format(amp)
        table = ru.build_dc_df(ru.vm_cols if include_delta_vm else [])
        amp_output = ru.concat_path(cell_out_dir, ru.get_dc_dir_name(9999,amp,trial)).replace('9999', '*')
        vm_rest = np.NaN

        for out_dir in glob.iglob(amp_output):
            dir_name = out_dir.split('/')[-1]
            el = int([x for x in dir_name.split('_') if x.startswith('el')][0][2:]) # parse el from folder name..
            config_path = ru.get_config_resolved_path(out_dir, el, amp)
            cvh5 = ru.get_cv_files(out_dir, [0])[0]
            conf = ru.get_json_from_file(config_path)
            waveform = stimx_waveform_factory(conf)

            electrodes_dir = conf['output']['electrodes_dir']
            electrodes_dir = ru.get_dir_root() + '/' + '/'.join(electrodes_dir.split('/')[2:])

            spikes = cvh5['spikes'].value
            el_xyz = ru.get_electrode_xyz(ru.get_electrode_path(electrodes_dir, cell_gid, el)).flatten()
            cell_xyz = ru.get_cell_xyz(glob.glob(out_dir + cell_csv_pattern)[0]).flatten()
            el_dist = np.linalg.norm(el_xyz - cell_xyz)
            run_id = ru.resolve_run_id(cell_gid, el, amp)

            try:
                vm_data = extract_vm_data(cvh5, waveform.delay, waveform.duration) if include_delta_vm else []
                vm_rest = vm_data.pop(0)
                data = [[trial, el], el_xyz, [el_dist, amp, spikes], vm_data]
                table.loc[run_id] = list(itertools.chain.from_iterable(data))
            except:
                print run_id, [el_dist, amp, spikes]
                raise

        filename = ru.get_table_filename(cell_gid, amp)
        print 'Data collected. Writing to {}...'.format(filename)
        fpath = ru.get_reobase_folder('Run_folder/result_tables', stim_type, filename)
        ru.write_table_h5(fpath, table, attrs={'has_vm_data':include_delta_vm,'vm_rest': vm_rest})
        print 'Done.'


def extract_vm_data(cvh5, delay, dur):
    dt = cvh5.attrs['dt']
    vm = cvh5['vm'].value
    spikes = cvh5['spikes'].value
    get_step = lambda x: int(x / dt)
    vm_rest = vm[get_step(delay - 500):get_step(delay - 5)].mean()

    if len(spikes) < 2: # ensure subthreshold or edge case
        vm_stim = vm[get_step(delay + dur - 500):get_step(delay + dur - 5)].mean()
    else:
        vm_stim = np.NaN

    return [vm_rest, vm_stim, (vm_stim - vm_rest)]


## Profiler output
#pr.disable()
#sortby = 'cumulative'
#ps = pstats.Stats(pr).strip_dirs().sort_stats(sortby)
#ps.print_stats()




