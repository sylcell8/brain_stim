import glob
import numpy as np
import itertools
import reobase_analysis.reobase_utils as ru
import reobase_analysis.sin_utils as su
from reobase_analysis.reobase_utils import StimType, ModelType, InputType
from isee_engine.bionet.stimxwaveform import stimx_waveform_factory
from isee_engine.bionet.stimxwaveform import iclamp_waveform_factory
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

def build_sin_dc(cell_gid, input_type, stim_type, model_type , inputs, trial, include_delta_vm = True,
                 include_sin = True, include_vm_phase_analysis=True, include_vext_phase_analysis=True,
                 saved_data= False):

    cell_csv_pattern = '/*_cel[ls]*csv'
    cell_out_dir = ru.get_output_dir(input_type, stim_type, model_type, cell_gid, saved_data)
    include_iclamp = input_type == "extrastim_intrastim"
    additional_cols = ru.resolve_additional_cols(include_delta_vm, include_sin, include_iclamp,
                                                 include_vm_phase_analysis, include_vext_phase_analysis)
    print additional_cols
    for amp in inputs:
        print 'Build data table for ex_amp = {}...'.format(amp)
        all_dir_name = ru.resolve_output_aggregates(include_delta_vm, include_sin, include_iclamp, amp, trial)
        amp_output =  ru.concat_path(cell_out_dir, all_dir_name)
        table = ru.build_df(additional_cols)
        vm_rest = np.NaN

        for out_dir in glob.iglob(amp_output):
            dir_name = out_dir.split('/')[-1]
            el = int([x for x in dir_name.split('_') if x.startswith('el')][0][2:])
            fq = int([x for x in dir_name.split('_') if x.startswith('freq')][0][4:])
            ic_amp = int([x for x in dir_name.split('_') if x.startswith('icamp')][0][5:]) * 0.001 if "icamp" in dir_name else None

            config_path = ru.get_config_resolved_path(stim_type, out_dir, el, amp, fq, ic_amp)
            run_id = ru.resolve_run_id(cell_gid, el, amp, fq, ic_amp)
            cvh5 = ru.get_cv_files(out_dir, [0])[0]

            conf = ru.get_json_from_file(config_path)
            electrodes_dir = ru.get_dir_root(saved_data) + '/' + '/'.join(conf['output']['electrodes_dir'].split('/')[2:])
            in_waveform = iclamp_waveform_factory(conf)

            spikes = cvh5['spikes'].value
            el_xyz = ru.get_electrode_xyz(ru.get_electrode_path(electrodes_dir, cell_gid, el)).flatten()
            ru.get_electrode_path(electrodes_dir, cell_gid, el)
            cell_xyz = ru.get_cell_xyz(glob.glob(out_dir + cell_csv_pattern)[0]).flatten()
            el_dist = round(np.linalg.norm(el_xyz - cell_xyz))

            try:
                vm_data = extract_vm_data( cvh5, in_waveform.delay, in_waveform.duration) if include_delta_vm else []
                vm_rest = vm_data.pop(0)
                vm_phase_analysis_data = extract_v_phase_analysis("vm",cvh5, in_waveform.delay, in_waveform.duration, fq)
                vext_phase_analysis_data = extract_v_phase_analysis("vext",cvh5, in_waveform.delay, in_waveform.duration, fq)

                data = [[trial, el], el_xyz, [el_dist, amp, spikes]]

                if include_delta_vm:
                    data = data + [vm_data]

                if include_sin:
                    data = data + [[fq * 1.0]]

                if include_iclamp:
                    data = data + [[ic_amp]]

                if include_vm_phase_analysis:
                    data = data + [vm_phase_analysis_data]


                if include_vext_phase_analysis:
                    data = data + [vext_phase_analysis_data]

                table.loc[run_id] = list(itertools.chain.from_iterable(data))
            except:
                print run_id, [el_dist, amp, spikes]
                raise

        index_close_els = ru.get_index_close_els(cell_gid, input_type, stim_type, model_type, saved_data)
        table = table.drop(index_close_els)
        table.loc[table["vm_phase"] < 0, "vm_phase"] = table["vm_phase"] + 360

        filename = ru.get_table_filename(cell_gid, amp, trial)
        print 'Data collected. Writing to {}...'.format(filename)
        fpath = ru.get_table_dir(input_type,stim_type, model_type, filename)
        print "writing to:" , fpath
        ru.write_table_h5(fpath, table, attrs={'has_vm_data': include_delta_vm,
                                               'vm_rest': vm_rest,
                                               'has_iclamp': include_iclamp,
                                               'has_sin': include_sin,
                                               'has_vm_phase_analysis':include_vm_phase_analysis,
                                               'has_vext_phase_analysis': include_vext_phase_analysis})
        print 'Done.'

def extract_v_phase_analysis(var_name ,cvh5, delay, dur, freq):

    spikes = cvh5['spikes'].value
    if len(spikes) < 1:
        var_amp, var_phase, var_mean = su.fit_sin_h5(var_name, cvh5, delay, dur, freq)
    else:
        var_amp = np.NaN
        var_phase = np.NaN

    if var_name=="vext":
        var_amp, var_phase, var_mean = su.fit_sin_h5(var_name, cvh5, delay, dur, freq)

    # print var_amp, var_phase, var_mean
    return [var_amp, var_phase]


def extract_vm_data(cvh5, delay, dur):
    dt = cvh5.attrs['dt']
    vm = cvh5['vm'].value
    spikes = cvh5['spikes'].value
    get_step = lambda x: int(x / dt)

    vm_rest = vm[get_step(delay - 500):get_step(delay - 5)].mean()

    if len(spikes) < 1: # ensure subthreshold or edge case
        vm_stim = vm[get_step(delay + 1000):get_step(delay + dur-5)].mean()
        if (dur) < 2000:
            print "ERROR in calculating vm_stim"
    else:
        vm_stim = np.NaN

    return [vm_rest,  vm_stim, (vm_stim - vm_rest)]


def build_dc(cell_gid, ex_inputs, input_type, stim_type, model_type , trial):
    cell_csv_pattern = '/*_cel[ls]*csv'  # ridiculous pattern matching for old files called 1_cell.csv vs new ones called [gid].csv
    cell_out_dir = ru.get_output_dir(stim_type, model_type, cell_gid)
    include_delta_vm = stim_type == StimType.DC.value

    for amp in ex_inputs:
        print 'Build data table for amp = {}...'.format(amp)
        table = ru.build_df(ru.vm_cols if include_delta_vm else [])
        amp_output = ru.concat_path(cell_out_dir, ru.get_dc_dir_name(9999, amp, trial)).replace('9999', '*')
        vm_rest = np.NaN

        for out_dir in glob.iglob(amp_output):
            dir_name = out_dir.split('/')[-1]
            el = int([x for x in dir_name.split('_') if x.startswith('el')][0][2:]) # parse el from folder name..
            config_path = ru.get_config_resolved_path(stim_type, out_dir, el, amp)
            cvh5 = ru.get_cv_files(out_dir, [0])[0]
            conf = ru.get_json_from_file(config_path)
            electrodes_dir = ru.get_dir_root() + '/' + '/'.join( conf['output']['electrodes_dir'].split('/')[2:] )
            waveform = stimx_waveform_factory(conf)

            spikes = cvh5['spikes'].value
            el_xyz = ru.get_electrode_xyz(ru.get_electrode_path(electrodes_dir, cell_gid, el)).flatten()
            cell_xyz = ru.get_cell_xyz(glob.glob(out_dir + cell_csv_pattern)[0]).flatten()
            el_dist = round(np.linalg.norm(el_xyz - cell_xyz))
            run_id = ru.resolve_dc_run_id(cell_gid, el, amp)


            try:
                vm_data = extract_vm_data(cvh5, waveform.delay, waveform.duration) if include_delta_vm else []
                vm_rest = vm_data.pop(0)
                data = [[trial, el], el_xyz, [el_dist, amp, spikes], vm_data]
                table.loc[run_id] = list(itertools.chain.from_iterable(data))
            except:
                print run_id, [el_dist, amp, spikes]
                raise

        filename = ru.get_table_filename(cell_gid, amp, trial)
        print 'Data collected. Writing to {}...'.format(filename)
        fpath = ru.get_table_dir(stim_type, model_type, filename)
        ru.write_table_h5(fpath, table, attrs={'has_vm_data':include_delta_vm,'vm_rest': vm_rest})
        print 'Done.'








