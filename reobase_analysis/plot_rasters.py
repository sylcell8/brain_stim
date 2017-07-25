import numpy as np
import matplotlib.pyplot as plt
import reobase_utils as r

fdir = r.get_reobase_folder('Run_folder/result_tables/')
cell_gid = 313862022

print "Fetching data..."
fetch_amps = map(str,range(10 ,80, 10))
paths = [r.concat_path(fdir, 'table_{}_amp{}.h5'.format(cell_gid, a)) for a in fetch_amps]

t = r.build_dc_df()
t = t.append([r.read_table_h5(p) for p in paths])
t['num_spikes'] = t.apply(lambda row: len(row['spikes']), axis=1)
print "Done"

#%% find raster for a given el, amp
#el = 10
#amp = -0.03
#spikes = t[(t['electrode'] == el) & (t['amp'] == amp)].spikes

# by amp

def plot_amp(amp):
    tamp = t[t['amp'] == amp]
    xs = np.array([])
    ys = np.array([])

    for rid, row in tamp.iterrows():
        num = row['num_spikes']
        el = row['electrode']
        spikes = row['spikes']
        xs = np.concatenate((xs, spikes))
        ys = np.concatenate((ys, [el ] *num))


    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(xs, ys,
                      marker='o', s=10, edgecolors='none')

    ax.set_title('Spike raster for amp = {}'.format(amp))
    ax.set_xlabel('Time')
    ax.set_ylabel('Electrode')
    plt.show()

plot_amp(-0.03)


# by el

def plot_el(el):

    tamp = t[t['electrode'] == el]
    xs = np.array([])
    ys = np.array([])

    for rid, row in tamp.iterrows():
        num = row['num_spikes']
        amp = row['amp']
        spikes = row['spikes']
        xs = np.concatenate((xs, spikes))
        ys = np.concatenate((ys, [amp ] *num))


    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(xs, ys,
                      marker='o', s=10, edgecolors='none')

    ax.set_title('Spike raster for el = {}'.format(el))
    ax.set_xlabel('Time')
    ax.set_ylabel('I_{stim}')
    plt.show()

plot_el(10)