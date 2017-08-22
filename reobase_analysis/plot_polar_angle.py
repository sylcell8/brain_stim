import matplotlib.pyplot as plt
import reobase_utils as r
import analysis as ra
import numpy as np
import pandas as pd
from reobase_analysis.analysis import StimType

SHOW = True

cell_gid = [313862022, 314900022, 320668879][1]
tdc = r.read_cell_tables(cell_gid, [str(x) for x in range(10,21,10)], stim_type=StimType.DC)
tdc['theta'], tdc['phi'] = ra.spherical_coords(tdc)
#tdcp = r.read_cell_tables(cell_gid, [str(x) for x in range(20,101,20)], stim_type=StimType.DC_LGN_POISSON)
#tdcp['theta'], tdcp['phi'] = ra.spherical_coords(tdcp)

#%%

def plot_spikes_polar_angle(t, amp, col_name = 'num_spikes', nbins=14):
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
    
    if SHOW:
        plt.show()
    else:
        plt.savefig('polar_angle_spikes_{}_'.format(cell_gid) + r.format_amp(amp) + '.png')

#%%
        
data = tdc
data = data[(data.distance == 35)] # exclude closest layer
#df = pd.DataFrame(index=data.electrode)

for amp, g in data.groupby('amp'):
#    print amp, g['num_spikes']
#    df[amp] = g['num_spikes']
    plot_spikes_polar_angle(g, amp, col_name='delta_vm')
