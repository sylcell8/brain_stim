import matplotlib.pyplot as plt
import reobase_utils as r
import analysis as ra
import numpy as np

cell_gid = 313862022
t = r.read_cell_tables(cell_gid, range(10,50,10))
t['num_spikes'] = t.apply(lambda row: len(row['spikes']), axis=1)


#%% Find spherical coordinates
# distance is 'r'
rho = np.sqrt(t.x**2 + t.y**2)
t['phi'] = phi2 = np.arctan2(rho, t.z)
t['theta'] = theta2 = np.arctan2(t.y,t.x)

#%% Find threshold
thresholds = ra.find_thresholds(t)
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


fig = plt.figure(figsize=(10,6))
ax = fig.add_subplot(111)
line = ax.scatter([get_theta(el) for el in els], [get_phi(el) for el in els], 
            c=thresh, s=14)
plt.colorbar(line)
ax.set_title('threshold at location in spherical coordinates')
ax.set_xlabel('theta')
ax.set_xticks(arctan2_range)
ax.set_xticklabels(arctan2_labels)
ax.set_yticks(arctan2_range[2:])
ax.set_yticklabels(arctan2_labels[2:])
plt.show()

#%%
fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter([get_phi(el) for el in els], thresh, s=4)
ax.set_title('threshold vs angle $\phi$ to z-axis')
ax.set_xticks(np.arange(0, np.pi+0.1, np.pi/2))
ax.set_xticklabels(arctan2_labels[2:])
plt.show()

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter([get_theta(el) for el in els], thresh, s=4)
ax.set_title('threshold vs angle $\Theta$ to x-axis')
ax.set_xticks(arctan2_range)
ax.set_xticklabels(arctan2_labels)
plt.show()

#%%

compare = t[['x','y','z','phi','theta','distance','amp','num_spikes']].cov().as_matrix()
np.fill_diagonal(compare, 0)

line = plt.matshow(compare)
plt.colorbar(line)
plt.show()




