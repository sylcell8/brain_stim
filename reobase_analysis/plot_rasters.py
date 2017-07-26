import numpy as np
import matplotlib.pyplot as plt
import reobase_utils as r

cell_gid = 313862022
t = r.read_cell_tables(cell_gid, [30])
t['num_spikes'] = t.apply(lambda row: len(row['spikes']), axis=1)

#%% find raster for a given el, amp

# by amp

def build_raster_data(slice_feature, value, y_feature):
    sub_df = t[t[slice_feature] == value]
    xs = np.array([]) # TODO preallocate
    ys = np.array([])

    for rid,row in sub_df.iterrows():
        el = row[y_feature]
        num = row['num_spikes']
        spikes = row['spikes']
        xs = np.concatenate((xs, spikes))
        ys = np.concatenate((ys, [el] *num))
        
    return xs, ys


def plot_amp(amp):
    xs, ys = build_raster_data('amp', amp, 'electrode')

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
    xs, ys = build_raster_data('electrode', el, 'amp')
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(xs, ys,
                      marker='o', s=10, edgecolors='none')

    ax.set_title('Spike raster for el = {}'.format(el))
    ax.set_xlabel('Time')
    ax.set_ylabel('$I_{stim}$')
    plt.show()

plot_el(10)



