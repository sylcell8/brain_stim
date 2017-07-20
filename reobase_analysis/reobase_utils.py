import h5py as h5
import pandas as pd
import numpy as np
import script.tchelpers as tc
import script.generate_utils as g

dc_cols = ['trial', 'electrode', 'x', 'y', 'z', 'distance', 'amp', 'spikes']

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
#     IO / folder and file names
#
#################################################

def get_spikes_data(out_path):
    cellvars = tc.get_cv_files(out_path, cells=[0])[0]
    return cellvars['spikes'].value


def get_electrode_xyz(electrode_pos_path):  # Ideally you would use the method bionet uses
    # mesh files are unnecessary for this study
    electrode_pos_df = pd.read_csv(electrode_pos_path, sep=' ')
    return electrode_pos_df.as_matrix(columns=['pos_x', 'pos_y', 'pos_z'])


def get_cell_xyz(cell_file):  # Ideally you would use the method bionet uses
    cell_props_df = pd.read_csv(cell_file, sep=' ')
    return cell_props_df.as_matrix(columns=['x_soma', 'y_soma', 'z_soma'])


def resolve_run_id(gid, electrode, i):
    stringified = map(str, [gid, electrode, '{0:.0f}'.format(np.abs(i * 1000))])
    return '_'.join(stringified)  # using current in micro amps


def get_electrode_path(electrodes_dir, gid, el):
    return '/'.join([electrodes_dir, gid + '_' + g.fill_el(el) + '.csv'])


def get_config_resolved_path(out_folder, el):
    return out_folder + 'config_el' + g.fill_el(el) + '_resolved.json'