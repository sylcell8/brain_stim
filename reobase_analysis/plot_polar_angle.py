import matplotlib.pyplot as plt
import reobase_utils as r
import analysis as ra
import numpy as np
import pandas as pd
from reobase_analysis.analysis import StimType

SAVE = False


def plot(t, amp, col_name='num_spikes', nbins=14, save_name=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('"{}" distribution by polar angle $\Theta$ (amp = {})'.format(col_name, amp))
    ax.set_xlabel('$\Theta$ (rad)')
    ax.set_ylabel(col_name)
    #    tc.set_theta_ticks(ax)

    n, bins = np.histogram(t.theta, bins=nbins)
#    width = bins[1] - bins[0]
    categories = pd.cut(t['theta'], bins)
    groups = t.groupby(categories)

    data = []
    rads = []

    for interval, g in groups:
        rads = rads + [interval.mid]
        data.append(g[col_name])

    ax.boxplot(data, showmeans=True)
    ax.set_xticklabels(["{0:.2f}".format(x) for x in np.array(rads)/np.pi])
    
    if save_name is not None:
        plt.savefig(save_name)
    else:
        plt.show()


def fetch_data_plot(cell_gid, amp, stim_type, *args, **kwargs):
    """ Same as 'plot' but fetches data for you """
    t = r.read_cell_tables(cell_gid, [amp], stim_type=stim_type)
    t['theta'], t['phi'] = ra.spherical_coords(t)
    plot(t, amp, *args, **kwargs)

#%%

def default():
    cell_gid = [313862022, 314900022, 320668879][1]
    t = r.read_cell_tables(cell_gid, [str(x) for x in range(10, 21, 10)], stim_type=StimType.DC)
    t['theta'], t['phi'] = ra.spherical_coords(t)

    # tdcp = r.read_cell_tables(cell_gid, [str(x) for x in range(20,101,20)], stim_type=StimType.DC_LGN_POISSON)
    # tdcp['theta'], tdcp['phi'] = ra.spherical_coords(tdcp)

    data = t
    data = data[(data.distance == 35)] # exclude closest layer


    for amp, g in data.groupby('amp'):
        # save_name = 'polar_angle_spikes_{}_'.format(cell_gid) + r.format_amp(amp) + '.png'
        plot(g, amp, col_name='delta_vm')



# default()