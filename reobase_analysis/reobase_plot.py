#import numpy as np
import matplotlib.pyplot as plt
import reobase_utils as ru
from mpl_toolkits.mplot3d import Axes3D

fpath = '/Volumes/aibs/mat/Taylorc/test_table.h5'


t = ru.read_table_h5(fpath)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
line = ax.scatter(t.x, t.y, t.z, c=t.spikes.map(lambda x: x.size), s=60, edgecolors='none')
cb = plt.colorbar(line)


def forceUpdate(event):
    global line
    line.changed()


fig.canvas.mpl_connect('draw_event', forceUpdate)

plt.show()