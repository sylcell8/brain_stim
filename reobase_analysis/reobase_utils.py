import h5py as h5
import pandas as pd

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