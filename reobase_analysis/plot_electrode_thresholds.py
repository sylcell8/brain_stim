import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import reobase_utils as r
import analysis as ra


fdir = r.get_reobase_folder('Run_folder/result_tables/')
cell_gid = 313862022

print "Fetching data..."
fetch_amps = map(str,range(10 ,80, 10))
paths = [r.concat_path(fdir, 'table_{}_amp{}.h5'.format(cell_gid, a)) for a in fetch_amps]

t = r.build_dc_df()
t = t.append([r.read_table_h5(p) for p in paths])
t['num_spikes'] = t.apply(lambda row: len(row['spikes']), axis=1)
print "Done"

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

