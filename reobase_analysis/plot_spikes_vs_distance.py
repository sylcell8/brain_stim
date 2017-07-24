#import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import reobase_utils as ru


fdir = ru.get_reobase_folder('Run_folder/result_tables/')

fetch_amps = map(str,range(10 ,80, 10))
paths = [fdir + 'table_313862022_amp' + a + '.h5' for a in fetch_amps]

t = pd.concat([ru.read_table_h5(p) for p in paths])

#t = ru.read_table_h5(fpath)

# cal num spikes
t['num_spikes'] = t.apply(lambda row: len(row['spikes']), axis=1)

#%% Plot

fig = plt.figure()
ax = fig.add_subplot(111)

offset = 0.75
amps = t.amp.unique()

for i, amp in enumerate(amps):
    o = i*offset - len(amps)/2
    data= t[t['amp'] == amp]
    line = ax.scatter(data.distance + o, data.num_spikes, 
                      marker='o', s=50, alpha=.20, edgecolors='none', 
                      label=str(amp))
    
ax.set_title('Distance vs. number of spikes')
ax.set_xlabel('Distance from center of soma')
ax.set_ylabel('Number of spikes')
ax.set_xticks(t.distance.unique())
legend = ax.legend(loc='upper right')
    
plt.show()
