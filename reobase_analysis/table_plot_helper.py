import numpy as np
import matplotlib as mlb
import matplotlib.pyplot as plt
import h5py


def groupby_plot(table, groupby_col, plotx, ploty):
    for groupcol, group in table.groupby(groupby_col):
        fig, ax = plt.subplots()
        ax.plot(group[plotx], group[ploty], marker='o', linestyle='', ms=10)
        ax.set_xlabel(plotx)
        ax.set_ylabel(ploty)
        ax.set_title('{}=  {}'.format(groupby_col, groupcol))
        ax.set_xlim([0,50])
        plt.show()