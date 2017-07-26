import matplotlib.pyplot as plt
import reobase_utils as r
import analysis as ra
import numpy as np

cell_gid = 313862022
t = r.read_cell_tables(cell_gid, range(10,50,10))
t['num_spikes'] = t.apply(lambda row: len(row['spikes']), axis=1)


#%% Find spherical coordinates
rho = np.sqrt(t.x**2 + t.y**2)
t['phi'] = phi2 = np.arctan2(rho, t.z)
t['theta'] = theta2 = np.arctan2(t.y,t.x)

#%% Find threshold
thresholds = ra.find_thresholds(t)

#%%
def get_phi(el):
    return t[t['electrode'] == el].phi[0]

def get_theta(el):
    return t[t['electrode'] == el].theta[0]

#%%

xy = []
for el,thresh in thresholds.items():
    if thresh is not None:
        xy.append((el,thresh[1]))
#        ax.plot([k,k],t,'k-',lw=1)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter([get_phi(x[0]) for x in xy],   [x[1] for x in xy], s=4)
ax.set_title('threshold vs angle $\phi$ to z-axis')
ax.set_xticks(np.arange(0, np.pi+0.1, np.pi/2))
ax.set_xticklabels(['$0$','$\pi /2$','$\pi$'])
plt.show()

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter([get_theta(x[0]) for x in xy], [x[1] for x in xy], s=4)
ax.set_title('threshold vs angle $\Theta$ to x-axis')
ax.set_xticks(np.arange(-np.pi, np.pi+0.1, np.pi/2))
ax.set_xticklabels(['$-\pi$', '$-\pi /2$','$0$','$\pi /2$','$\pi$'])
plt.show()

#%%
fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter([get_theta(x[0]) for x in xy], [get_phi(x[0]) for x in xy], c=[x[1] for x in xy], s=4)
ax.set_title('threshold at location in spherical coordinates')
ax.set_xticks(np.arange(-np.pi, np.pi+0.1, np.pi/2))
ax.set_xticklabels(['$-\pi$', '$-\pi /2$','$0$','$\pi /2$','$\pi$'])
plt.show()