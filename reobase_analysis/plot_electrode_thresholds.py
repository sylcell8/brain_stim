import matplotlib.pyplot as plt
import reobase_utils as r
import analysis as ra
import numpy as np
import pandas as pd

#cell_gid = 313862022
#cell_gid = 314900022
cell_gid = 320668879
t = r.read_cell_tables(cell_gid, range(10,80,10))
t['num_spikes'] = t.apply(lambda row: len(row['spikes']), axis=1)
t['theta'], t['phi'] = ra.spherical_coords(t)

#%% Find threshold
thresholds = ra.find_thresholds(t)
# Choose upper value of range
el_th = []
for el,thresh in thresholds.items():
    if thresh is not None:
        el_th.append((el, thresh[1]))

[els, thresh] = zip(*el_th)

#%%
def get_phi(el):
    return t[t['electrode'] == el].phi[0]

def get_theta(el):
    return t[t['electrode'] == el].theta[0]


#%%

arctan2_range = np.arange(-np.pi, np.pi + 0.1, np.pi / 2)
arctan2_labels = ['$-\pi$', '$-\pi /2$', '$0$', '$\pi /2$', '$\pi$']

def set_theta_ticks(ax, xy='x'):
    if xy == 'x':
        ax.set_xticks(arctan2_range[2:])
        ax.set_xticklabels(arctan2_labels[2:])
    else:    
        ax.set_yticks(arctan2_range[2:])
        ax.set_yticklabels(arctan2_labels[2:])

    return ax


def set_phi_ticks(ax, xy='x'):
    if xy == 'x':
        ax.set_xticks(arctan2_range)
        ax.set_xticklabels(arctan2_labels)
    else:
        ax.set_yticks(arctan2_range)
        ax.set_yticklabels(arctan2_labels)

    return ax

def plot_threshold_angle(els, thresh):

    fig = plt.figure(figsize=(10,6))
    ax = fig.add_subplot(111)
    line = ax.scatter([get_phi(el) for el in els], [get_theta(el) for el in els],
                c=thresh, s=14)
    plt.colorbar(line)
    ax.set_title('threshold at location in spherical coordinates')
    ax.set_xlabel('theta')
    set_phi_ticks(ax)
    set_theta_ticks(ax, 'y')
    plt.show()

#%%
def plot_phi():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter([get_phi(el) for el in els], thresh, s=4)
    ax.set_title('threshold vs angle $\phi$ to z-axis')
    set_phi_ticks(ax)
    plt.show()

def plot_theta():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter([get_theta(el) for el in els], thresh, s=4)
    ax.set_title('threshold vs angle $\Theta$ to x-axis')
    set_theta_ticks(ax)
    plt.show()

#%%
def table_covariance(t):
    compare = t[['x','y','z','phi','theta','distance','amp','num_spikes']].cov().as_matrix()
    np.fill_diagonal(compare, 0)
    
    line = plt.matshow(compare)
    plt.colorbar(line)
    plt.show()

#table_covariance(t)

#%% Something new
    
def plot_spikes_polar_angle(t, nbins=14):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Number of spikes per electrode by polar angle $\Theta$')
    ax.set_xlabel('$\Theta$ (rad)')
    ax.set_ylabel('Average number of spikes')
#    set_theta_ticks(ax)
   
    n, bins = np.histogram(t.theta, bins=nbins)
    width = bins[1] - bins[0]
    categories = pd.cut(t['theta'], bins)
    groups = t.groupby(categories)
    
    for interval, g in groups:
        total_spikes = g['num_spikes'].sum()
        num_els = g['electrode'].unique().size
        spikes_per_el = float(total_spikes) / num_els
        ax.bar(interval.left, spikes_per_el, width)
        
    plt.savefig('polar_angle_spikes_{}_'.format(cell_gid) + r.format_amp(amp) + '.png') # amp is in outside scope
    

for amp, g in t.groupby('amp'):
    plot_spikes_polar_angle(g)

