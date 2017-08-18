#import os,sys
import glob
import numpy as np
import reobase_analysis.reobase_utils as ru
from reobase_analysis.analysis import StimType
from isee_engine.bionet.stimxwaveform import stimx_waveform_factory

#import cProfile, pstats, io
#pr = cProfile.Profile()
#pr.enable()

"""
Script to build h5 files containing organized run info for all runs of a particular amplitude
Will include all electrodes. Has no overwrite protection
"""

### Params ###
default_gid = [313862022, 314900022, 320668879][0]
default_inputs = [-0.01,-0.02,-0.03,-0.04,-0.05,-0.06,-0.07,-0.08,-0.09,-0.10]
default_stim_type = StimType.DC_LGN_POISSON
default_cell_csv_pattern = '/*_cell.csv'

def build(cell_gid, inputs, stim_type, trial=0):
    cell_out_dir = ru.get_reobase_folder('Run_folder/outputs', stim_type, cell_gid)

    for amp in inputs:

        print 'Build table for amp = {}...'.format(amp)
        table = ru.build_dc_df()
        amp_output = ru.concat_path(cell_out_dir, ru.get_dc_dir_name(9999,amp,trial)).replace('9999', '*')

        for out_folder in glob.iglob(amp_output):
            out_dir = out_folder.split('/')[-1]
            el = int([x for x in out_dir.split('_') if x.startswith('el')][0][2:]) # parse el from folder name..
            config_path = ru.get_config_resolved_path(out_folder, el, amp)
            conf = ru.get_json_from_file(config_path)

            electrodes_dir = conf['output']['electrodes_dir']
            electrodes_dir = ru.get_dir_root() + '/' + '/'.join(electrodes_dir.split('/')[2:])

            waveform = stimx_waveform_factory(conf)
            amp = waveform.amp # use amp from source of truth
            spikes = ru.get_spikes_data(out_folder)
            el_xyz = ru.get_electrode_xyz(ru.get_electrode_path(electrodes_dir, cell_gid, el)).flatten()
            cell_xyz = ru.get_cell_xyz(glob.glob(out_folder + default_cell_csv_pattern)[0]).flatten()
            el_dist = np.linalg.norm(el_xyz - cell_xyz)
            run_id = ru.resolve_run_id(cell_gid, el, amp)

            try:
                table.loc[run_id] = [trial, el, el_xyz[0], el_xyz[1], el_xyz[2], el_dist, amp, spikes]
            except:
                print run_id, [trial, el, el_xyz[0], el_xyz[1], el_xyz[2], el_dist, amp, spikes]
                raise

        print 'Data collected. Writing h5...'
        fpath = ru.get_reobase_folder('Run_folder/result_tables', stim_type, ru.get_table_filename(cell_gid, amp))
        ru.write_table_h5(fpath, table)
        print 'Done.'

# print "Try: build(default_gid, inputs=default_inputs[:5], stim_type=default_stim_type)"

## Profiler output
#pr.disable()
#sortby = 'cumulative'
#ps = pstats.Stats(pr).strip_dirs().sort_stats(sortby)
#ps.print_stats()




