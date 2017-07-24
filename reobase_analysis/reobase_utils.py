import os
import math
import glob
import json
import h5py as h5
import numpy as np
import pandas as pd

import tchelpers as tc

#################################################
#
#     Run aggregate data output file
#
#################################################

dc_cols = ['trial', 'electrode', 'x', 'y', 'z', 'distance', 'amp', 'spikes']

def resolve_run_id(gid, electrode, i):
    stringified = map(str, [gid, electrode, '{0:.0f}'.format(np.abs(i * 1000))])
    return '_'.join(stringified)  # using current in micro amps

def build_dc_df():

    df = pd.DataFrame(columns=dc_cols)
    # pd doesn't do a great job of indentifying ints
    df['trial'] = df['trial'].astype(int)
    df['electrode'] = df['electrode'].astype(int)

    return df


def read_table_h5(fpath):
    table = build_dc_df()

    with h5.File(fpath, 'r') as f5:
        ids = f5['ids'].value
        spike_data = f5['spikes']

        for i, rid in enumerate(ids):  # i is key for f5 dsets, rid is key for spikes & df
            data_cols = [x for x in dc_cols if x != 'spikes']
            data = [f5[c][i] for c in data_cols]
            spikes = spike_data[rid].value

            table.loc[rid] = data + [spikes]

    return table


def write_table_h5(fpath, df):
    with h5.File(fpath, 'w') as f5:
        f5.create_dataset('ids', data=map(str, df.index))

        for col in df.columns:
            if col != 'spikes': # cuz it will explode if it is type 'object'
                f5.create_dataset(col, data=df[col])

        spike_grp = f5.create_group('spikes')
        for (rid, spike_times) in df.spikes.iteritems():
            spike_grp.create_dataset(rid, maxshape=(None,), chunks=True, data=spike_times)



#################################################
#
#     Paths / filenames
#
#################################################

def concat_path(*args):
    """
    join peices of paths together worry-free
    """
    root = args[0]
    is_abs_path = root[0] == '/'
    clean = [s.strip('/') for s in args]
    if is_abs_path:
        clean[0] = '/' + clean[0]
    return '/'.join(clean)

def format_el(el): #idempotent
    """
    formatting for el number for cleaner organization
    """
    return str(el).zfill(4)

def get_dc_key(el, amp):
    """
    file/folder name code
    """
    parts = ['el' + format_el(el), "amp{0:.0f}".format(math.fabs(amp * 1000.))]
    return '_'.join(parts)

def dc_folder_format(el, amp, trial):
    parts = [get_dc_key(el, amp), 'tr' + str(trial)]
    return '_'.join(parts)

def get_reobase_folder(*args):
    network_root = '/allen'
    if os.path.isdir('/Volumes'):
        network_root = '/Volumes'

    return concat_path(network_root, 'aibs/mat/Fahimehb/Data_cube/reobase', *args)

def get_electrode_path(electrodes_dir, gid, el):
    return '/'.join([electrodes_dir, gid + '_' + format_el(el) + '.csv'])


def get_config_resolved_path(out_folder, el, amp):
    return concat_path(out_folder, 'config_' + get_dc_key(el, amp) + '_resolved.json')



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
        files = [h5.File(f) for f in glob.glob(cv_dir + "*.h5")]

    return files

def get_json_from_file(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_spikes_data(out_path):
    cellvars = get_cv_files(out_path, cells=[0])[0]
    return cellvars['spikes'].value


def get_electrode_xyz(electrode_pos_path):  # Ideally you would use the method bionet uses
    # mesh files are unnecessary for this study
    electrode_pos_df = pd.read_csv(electrode_pos_path, sep=' ')
    return electrode_pos_df.as_matrix(columns=['pos_x', 'pos_y', 'pos_z'])


def get_cell_xyz(cell_file):  # Ideally you would use the method bionet uses
    cell_props_df = pd.read_csv(cell_file, sep=' ')
    return cell_props_df.as_matrix(columns=['x_soma', 'y_soma', 'z_soma'])

