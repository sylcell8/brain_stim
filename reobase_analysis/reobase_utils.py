import os
import math
import glob
import json
import h5py as h5
import numpy as np
import pandas as pd
from enum import Enum

"""
Many utils. Most are for building paths or file names or dealing with IO. 
These functions solidify the contract between the data and the simulation/analysis and are used everywhere that data 
is used--so best to be careful when changing the contract. 
Ideally utils are as small as possible--a single unit of work--so that you can easily compose them.
Names:
get...dir  -> returns path to a directory. last param *args allows additional paths to be added, with the exception of
            specific dc/sin/etc output dirs, since these are basically endpoints
get...path -> returns path to a file
resolve... -> the function is essentially a definition for whatever it outputs
"""


#################################################
#
#     Enumerated constant values
#
#################################################

# Enumerate stim types to use as source of truth
# Note: despite what it may look like elsewhere StimType.DC != 'dc' (!)
# Enumerate model types to use as source of truth

class Name(Enum):
    def __str__(self):
        return str(self.value)


class StimType(Name):
    DC = 'dc'
    DC_LGN_POISSON = 'dc_lgn_poisson'


class ModelType(Name):
    PERISOMATIC = 'perisomatic'
    ACTIVE      = 'all_active'
    PASSIVE     = 'passive'
    FAHIMEH     = 'fahimeh_passive'


#################################################
#
#     Paths / filenames
#
#################################################

def format_el(el):
    """ Formatting for el number for cleaner organization. Idempotent """
    return str(el).zfill(4)

def format_amp(amp):
    """ Formatting of amp for easier naming. Idempotent """
    return amp if type(amp) == str else "{0:.0f}".format( math.fabs(amp * 1000.) )

def format_freq(freq):
    """ Formatting of freq for naming. Idempotent. """
    return freq if type(freq) == str else "{0:.0f}".format(freq)

def get_dir_root():
    """ For dealing with different netweork locations on Mac/Linux """
    network_root = '/allen'
    if os.path.isdir('/Volumes'):
        network_root = '/Volumes'

    return network_root

def concat_path(*args):
    """ Join paths together by parts, worry-free """
    root = args[0]
    is_abs_path = root[0] == '/'
    clean = [str(s).strip('/') for s in args]
    if is_abs_path:
        clean[0] = '/' + clean[0]
    return '/'.join(clean)

def get_reobase_dir(*args):
    network_root = get_dir_root()
    return concat_path(network_root, 'aibs/mat/Fahimehb/Data_cube/reobase', *args)

def get_output_dir(stim_type, model_type, cell_gid, *args):
    """ Get dir containing runs for given params """
    reobase_dir = get_reobase_dir()
    return concat_path(reobase_dir, 'Run_folder/outputs/', stim_type, model_type, cell_gid, *args)

def get_electrode_path(electrodes_dir, gid, el):
    return concat_path(electrodes_dir, str(gid) + '_' + format_el(el) + '.csv')

def get_config_resolved_path(out_folder, el, amp):
    key = resolve_dc_key(el, amp)
    return concat_path(out_folder, 'config_' + key + '_resolved.json')

### DC ###

def resolve_dc_key(el, amp):
    """ file/folder name code """
    parts = ['el' + format_el(el), 'amp' + format_amp(amp)]
    return '_'.join(parts)

def get_dc_dir_name(el, amp, trial):
    return '_'.join([resolve_dc_key(el, amp), 'tr' + str(trial)])

def get_dc_output_dir(cell_gid, el, amp, model_type=ModelType.PERISOMATIC, trial=0):
    root_dir = get_output_dir(StimType.DC, model_type, cell_gid)
    out_dir = get_dc_dir_name(el, amp, trial)
    return concat_path(root_dir, out_dir)

### SIN ###

def resolve_sin_key(el, amp, freq):
    """ file/folder name code """
    parts = ['el' + format_el(el), 'amp' + format_amp(amp), 'freq' + format_freq(freq)]
    return '_'.join(parts)

def get_sin_dir_name(el, amp, freq, trial):
    return '_'.join([resolve_sin_key(el, amp, freq), 'tr' + str(trial)])

def get_sin_output_dir(cell_gid, el, amp, freq, model_type=ModelType.PERISOMATIC, trial=0):
    root_dir = get_output_dir(StimType.SIN, model_type, cell_gid)
    out_dir = get_sin_dir_name(el, amp, freq, trial)
    return concat_path(root_dir, out_dir)

### Tables ###

def get_table_dir(stim_type, model_type, *args):
    return get_reobase_dir('Run_folder/result_tables/', stim_type, model_type, *args)

def get_table_filename(cell_gid, amp):
    return 'table_{}_amp{}.h5'.format(cell_gid, format_amp(amp))


#################################################
#
#     IO / data
#
#################################################

def get_spikes_file(output):
    return h5.File(concat_path(output, 'spikes.h5'), 'r')


def get_cv_files(output, cells=None):
    cv_dir = concat_path(output, 'cellvars')

    if cells is not None:
        files = map(lambda c: h5.File(concat_path(cv_dir, str(c)) + '.h5', 'r'), cells)
    else:
        files = [h5.File(f) for f in glob.glob(cv_dir + "/*.h5")]

    return files

def get_json_from_file(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_spikes_data(out_path):
    cellvars = get_cv_files(out_path, cells=[0])[0]
    return cellvars['spikes'].value

def get_spikes_data2(out_path):
    ## UNTESTED! hoping this will be faster than using cv files.......
    ## TODO finish
    spikes = pd.read_csv(concat_path(out_path,'spikes.txt'), ' ')
    cellvars = get_cv_files(out_path, cells=[0])[0]
    return cellvars['spikes'].value

def get_electrode_xyz(electrode_pos_path):  # Ideally you would use the method bionet uses
    # mesh files are unnecessary for this study
    electrode_pos_df = pd.read_csv(electrode_pos_path, sep=' ')
    return electrode_pos_df.as_matrix(columns=['pos_x', 'pos_y', 'pos_z'])


def get_cell_xyz(cell_file):  # Ideally you would use the method bionet uses
    cell_props_df = pd.read_csv(cell_file, sep=' ')
    return cell_props_df.as_matrix(columns=['x_soma', 'y_soma', 'z_soma'])


#################################################
#
#     Run aggregate data output file
#
#################################################

dc_cols = ['trial', 'electrode', 'x', 'y', 'z', 'distance', 'amp', 'spikes']
vm_cols = ['vm_stim', 'delta_vm']

def resolve_run_id(gid, electrode, amp):
    """ Unique run id (per stim type) """
    stringified = map(str, [gid, electrode, format_amp(amp)])
    return '_'.join(stringified)  # using current in micro amps

def build_dc_df(additional_cols=[]):
    """ Wrapped df creation to give place to explicitly declare column types """
    df = pd.DataFrame(columns=(dc_cols + additional_cols))
    # pd doesn't do a great job of identifying ints
    df['trial'] = df['trial'].astype(int)
    df['electrode'] = df['electrode'].astype(int)

    return df


def read_table_h5(fpath):
    """ h5 to dataframe """

    with h5.File(fpath, 'r') as f5:
        extra_cols = vm_cols if 'has_vm_data' in f5.attrs and f5.attrs['has_vm_data'] else []
        table = build_dc_df(extra_cols)
        ids = f5['ids'].value
        spike_data = f5['spikes']

        for i, rid in enumerate(ids):  # i is key for f5 dsets, rid is key for spikes & df
            data_cols = (dc_cols + extra_cols)
            spike_index = data_cols.index('spikes')
            data_cols.pop(spike_index)
            data = [f5[c][i] for c in data_cols]
            # place spikes in correct position
            data.insert(spike_index, spike_data[rid].value)
            table.loc[rid] = data

    return table


def write_table_h5(fpath, df, attrs=None):
    """ dataframe to h5 """
    df.sort_values('electrode', inplace=True)
    with h5.File(fpath, 'w') as f5:
        f5.create_dataset('ids', data=map(str, df.index))

        for col in df.columns:
            if col != 'spikes': # cuz it will explode if it is type 'object'
                f5.create_dataset(col, data=df[col])

        spike_grp = f5.create_group('spikes')
        for (rid, spike_times) in df.spikes.iteritems():
            spike_grp.create_dataset(rid, maxshape=(None,), chunks=True, data=spike_times)

        if attrs is not None:
            for k,v in attrs.iteritems():
                f5.attrs[k] = v


def read_cell_tables(cell_gid, amp_range, stim_type,
                     data_dir=None):
    """ Read h5 files for a set of amplitudes """
    print "Fetching data..."

    data_dir = get_table_dir(stim_type, ModelType.PERISOMATIC) if data_dir is None else data_dir
    paths = [concat_path(data_dir, get_table_filename(cell_gid, a)) for a in amp_range]

    t = build_dc_df()  # do this for code analysis
    t = t.append([read_table_h5(p) for p in paths])
    t['num_spikes'] = t.apply(lambda row: len(row['spikes']), axis=1)

    print "Done"
    return t


def read_cell_rows(cell_gid, els, amps, stim_type='dc',
                   data_dir=None):
    """
    Read h5 files for a set of amps and electrodes -- faster when considering a small subset of electrodes
    Doesn't use read_table_h5--it actually interfaces with h5 file.
    """
    data_dir = get_table_dir(stim_type, ModelType.PERISOMATIC) if data_dir is None else data_dir
    els = [els] if type(els) is not list else els
    amps = [amps] if type(amps) is not list else amps # non-formatted
    data_cols = [x for x in dc_cols if x != 'spikes']
    table = build_dc_df()

    for amp in amps:
        fpath = concat_path(data_dir, get_table_filename(cell_gid, amp))

        with h5.File(fpath, 'r') as f5:
            ids = f5['ids'].value
            spike_data = f5['spikes']

            for el in els:
                rid = resolve_run_id(cell_gid,el,amp)
                i = np.argwhere(ids == rid)[0][0] # i is key for f5 dsets, rid is key for spikes & df
                data = [f5[c][i] for c in data_cols]
                table.loc[rid] = data + [(spike_data[rid].value)]

    table['num_spikes'] = table.apply(lambda row: len(row['spikes']), axis=1)

    return table