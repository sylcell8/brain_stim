import matplotlib.pyplot as plt
import reobase_utils as r
import analysis as ra

cell_gid = 313862022
t = r.read_cell_tables(cell_gid)
t['num_spikes'] = t.apply(lambda row: len(row['spikes']), axis=1)

#%% Find threshold
thresholds = ra.find_thresholds(t)

#%%
fig = plt.figure()
ax = fig.add_subplot(111)
xy = []
for k,t in thresholds.items():
    if t is not None:
        xy.append((k,t[1]))
#        ax.plot([k,k],t,'k-',lw=1)
        
ax.scatter([x[0] for x in xy], [x[1] for x in xy], s=4)