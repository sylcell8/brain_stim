#import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import reobase_utils as ru

cell_gid = [313862022, 314900022, 320668879][1]
stim_type='dc_lgn_poisson'

t = ru.read_cell_tables(cell_gid, stim_type=stim_type)
# add num spikes
t['num_spikes'] = t.apply(lambda row: len(row['spikes']), axis=1)


#%% Plot
def plot(t):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    offset = 0.75
    amps = t.amp.unique()
    
    for i, amp in enumerate(amps):
        o = i*offset - len(amps)/2
        data= t[t['amp'] == amp]
        ax.scatter(data.distance + o, data.num_spikes, 
                          marker='o', s=50, alpha=.20, edgecolors='none', 
                          label=str(amp))
        
    ax.set_title('Distance vs. number of spikes')
    ax.set_xlabel('Distance from center of soma')
    ax.set_ylabel('Number of spikes')
    ax.set_xticks(t.distance.unique())
    legend = ax.legend(loc='upper right')
        
    plt.show()

print "Run 'plot(t)'..."
#plot()