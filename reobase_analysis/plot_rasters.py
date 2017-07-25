import numpy as np
import matplotlib.pyplot as plt
import reobase_utils as r

cell_gid = 313862022
t = r.read_cell_tables(cell_gid)
t['num_spikes'] = t.apply(lambda row: len(row['spikes']), axis=1)

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

#plot_amp(-0.03)


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

#plot_el(10)