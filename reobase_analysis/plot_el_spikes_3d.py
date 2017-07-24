import numpy as np
import matplotlib.pyplot as plt
import reobase_utils as ru
from mpl_toolkits.mplot3d import Axes3D

fpath = '/Volumes/aibs/mat/Taylorc/test_table.h5'

from allensdk.core.cell_types_cache import CellTypesCache
ctc = CellTypesCache(manifest_file='cell_types/manifest.json')
morphology = ctc.get_reconstruction(313862022)
soma = morphology.compartment_index[0]

# soma -- NOT A REAL RADIUS
u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
r = soma['radius']
x = r * np.cos(u)*np.sin(v)
y = r * np.sin(u)*np.sin(v)
z = r * np.cos(v)

t = ru.read_table_h5(fpath)

#%% Plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
line = ax.scatter(t.x, t.y, t.z, c=t.spikes.map(lambda x: x.size), s=50, edgecolors='none')
ax.plot_wireframe(x, y, z, color="r")
cb = plt.colorbar(line)


def forceUpdate(event):
    global line
    line.changed()


fig.canvas.mpl_connect('draw_event', forceUpdate)

plt.show()