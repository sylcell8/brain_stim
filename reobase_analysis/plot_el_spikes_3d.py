import numpy as np
import matplotlib.pyplot as plt
import reobase_utils as ru
from mpl_toolkits.mplot3d import Axes3D

cell_gid = [313862022, 314900022, 320668879][1]
t = ru.read_cell_tables(cell_gid, [str(x) for x in [30,40]], stim_type='dc_lgn_poisson')

#%% Do morphology stuff

#from allensdk.core.cell_types_cache import CellTypesCache
#ctc = CellTypesCache(manifest_file='cell_types/manifest.json')
#morphology = ctc.get_reconstruction(cell_gid)
#soma = morphology.compartment_index[0]

# soma sphere model
u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
r = 7 #soma['radius']
x = r * np.cos(u)*np.sin(v)
y = r * np.sin(u)*np.sin(v)
z = r * np.cos(v)

#%% Plot
amp = -0.04
sub = t[(t['amp'] == amp) & (t['electrode'] <= 550)]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
line = ax.scatter(sub.x, sub.y, sub.z, c=sub.spikes.map(lambda x: x.size), 
                  s=50, edgecolors='none')
ax.plot_wireframe(x, y, z, color="r")
cb = plt.colorbar(line)


def forceUpdate(event):
    global line
    line.changed()


fig.canvas.mpl_connect('draw_event', forceUpdate)

plt.show()


#%% Plot stuff

t['theta'], t['phi'] = ra.spherical_coords(t)

amp = -0.03
threshold = 0

t2 = t[(t['phi'] > 3*np.pi/4) | (t['phi'] < np.pi/4)]

def yes_no(df):
    
    yes = df[(df['amp'] == amp) & (df['num_spikes'] >  threshold)]
    no  = df[(df['amp'] == amp) & (df['num_spikes'] <= threshold)]
    
    return yes,no

yes,no = yes_no(t2)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
line = ax.scatter(yes.x, yes.y, yes.z, c='g', s=50, edgecolors='none')
line = ax.scatter(no.x, no.y, no.z, c='grey', s=50, edgecolors='none')

plt.show()