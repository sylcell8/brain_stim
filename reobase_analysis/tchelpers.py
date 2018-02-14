import numpy as np
import matplotlib as mlb
import matplotlib.pyplot as plt
import h5py
from allensdk.core.cell_types_cache import CellTypesCache

from reobase_utils import *

"""
A set of plots and plot helpers. More useful and important to build are the 
plot helpers, which then you can use over and over to build a particular axis 
to modify a particular axis' ticks or legend or something.
Best for the top level implementation to sit in the analysis file for any important plot.
NOTE: importing this script will change your MPL defaults. See the customzing section below
TODO: change the name :)
"""


#################################################
#
#     Customizing plot params
#
#################################################

# size: Either an relative value of 'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large' 
# or an absolute font size, e.g., 12
# default_plot_config = {
#     'title_fontsize':14,
#     'tick_fontsize':2,
#     'axis_fontsize':2
# }

# global config
mlb.rcParams.update({
    'figure.titlesize'    : 'xx-large',
    'axes.titlesize'      : 'x-large',   # fontsize of the axes title
    'axes.labelsize'      : 'large',  # fontsize of the x any y labels
    # 'xtick.labelsize'     : 'medium',
    # 'ytick.labelsize'     : 'medium',
    # 'legend.fontsize'     : 'medium',
})

# Consider for a single plot...
# with plt.rc_context({"axes.grid": True, "grid.linewidth": 0.75}):
#     f, ax = plt.subplots()  # Will make a figure with a grid
#     ax.plot(x, y)


#################################################
#
#     Plot helpers
#
#################################################


def get_cellvar_timeseries_plot(output, var_name, ax=None, cell=None, size=(13, 7),
                                ticks_every=500, show_legend=True, **kwargs):

    cvfiles = get_cv_files(output, [cell]) if cell is not None else get_cv_files(output)
    tstop = cvfiles[0].attrs['tstop']
    dt = cvfiles[0].attrs['dt']
    #var = []
    if not ax:
        plt.figure(figsize=size)
        ax = plt.subplot(111)
    for i, f in enumerate(cvfiles):
        plot_args = {}
        plot_args['label'] = 'cell_' + str(i) if 'label' not in kwargs else kwargs['label']
        plot_args['c'] = kwargs['c'] if 'c' in kwargs else None
        ax.plot(np.arange(0,tstop,dt), f[var_name].value, lw=2.5, **plot_args)
    #    var.append(f[var_name].value)
    xtick_location, xtick_labels = calc_xticks([0, tstop], ticks_every)
    ax.set_xticks(xtick_location)
    ax.set_xticklabels(xtick_labels)
    
    if show_legend:
        ax.legend(loc='upper left')
    return ax
    # return var, ax

def get_spikes_raster_plot(output, size=None, ax=None, ticksEvery=500, **kwargs):

    if not ax:
        plt.figure(figsize=size)
        ax = plt.subplot(111)

    f_spikes = get_spikes_file(output)
    tstart = f_spikes.attrs['tstart'] # ms
    tstop = f_spikes.attrs['tstop'] # ms
    cells = [int(i) for i in f_spikes.keys()]

    for c, times in f_spikes.items():
        n = times.size
        ids = [int(c)] * n
        ax.scatter(times.value.tolist(), ids, s=16, lw=0)

    ax.margins(0.05, 0.50)
    ax.set_xlabel('Time (s)')

    xtick_location, xtick_labels = calc_xticks([0, tstop],ticksEvery)
    ax.set_xticks(xtick_location)
    ax.set_xticklabels(xtick_labels)
    ax.set_yticks(cells)
    ax.set_yticklabels(['cell_' + str(c) for c in cells])

    if all([x.value.size == 0 for x in f_spikes.values()]):
        ax.text(0.4, 0.5, 'No spikes recorded', fontsize=15, transform=ax.transAxes)

    return ax

def get_cell_morphology_plot(cell_id, size=(10,10), ax=None):
    # from allensdk.core.swc import Marker
    # import pprint

    if not ax:
        plt.figure(figsize=size)
        ax = plt.subplot(111)

    ctc = CellTypesCache(manifest_file='cell_types/manifest.json')
    morphology = ctc.get_reconstruction(cell_id)
    # markers = ctc.get_reconstruction_markers(cell_id)

    for n in morphology.compartment_list:
        for c in morphology.children_of(n):
            ax.plot([n['x'], c['x']], [n['y'], c['y']], color='black')

    return ax

#################################################
#
#     Axis labels and ticks
#
#################################################

zero_to_pi_range = np.arange(-np.pi, np.pi + 0.1, np.pi / 2)
zero_to_pi_labels = ['$-\pi$', '$-\pi /2$', '$0$', '$\pi /2$', '$\pi$']

def set_theta_ticks(ax, xy='x'):
    if xy == 'x':
        ax.set_xticks(zero_to_pi_range[2:])
        ax.set_xticklabels(zero_to_pi_labels[2:])
    else:
        ax.set_yticks(zero_to_pi_range[2:])
        ax.set_yticklabels(zero_to_pi_labels[2:])

    return ax


def set_phi_ticks(ax, xy='x'):
    if xy == 'x':
        ax.set_xticks(zero_to_pi_range)
        ax.set_xticklabels(zero_to_pi_labels)
    else:
        ax.set_yticks(zero_to_pi_range)
        ax.set_yticklabels(zero_to_pi_labels)

    return ax


def calc_xticks(tlimits,ticksEvery):
    xtick_location = np.arange(tlimits[0], tlimits[1] + 1, ticksEvery)
    xtick_labels = map(lambda t: str(t / 1000.), xtick_location)
    return xtick_location, xtick_labels

#################################################
#
#     Plots
#
#################################################


def plot_vm(output, **kwargs):
    ax = get_cellvar_timeseries_plot(output, 'vm', **kwargs)
    ax.set_title('Membrane Voltage')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('$V_m$ (mV)')
    plt.show()


def plot_vext(output, **kwargs):
    ax = get_cellvar_timeseries_plot(output, 'vext', **kwargs)
    ax.set_title('External Voltage')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('$V_{ext}$ (mV)')
    plt.show()

def plot_im(output, **kwargs):
    ax = get_cellvar_timeseries_plot(output, 'im', **kwargs)
    ax.set_title('Membrane Current')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('$I_m$ (mA)')
    plt.show()

def plot_vext_vm_tiles(outputs, **kwargs):
    if type(outputs) is str:
        outputs = [outputs]

    fig, axarr = plt.subplots(2,len(outputs), sharex='col', sharey='row', figsize=(13,7))

    kwargs['size'] = None
    kwargs['show_legend'] = False

    for i,fname in enumerate(outputs):
        if len(axarr.shape) is 1:
            (ax_vext, ax_vm) = (axarr[0], axarr[1])
        else:
            (ax_vext, ax_vm) = (axarr[0][i], axarr[1][i])

        kwargs['ax'] = ax_vext
        get_cellvar_timeseries_plot(fname, 'vext', **kwargs)
        ax_vext.set_xlabel('Time (s)')
        ax_vext.set_ylabel('$V_{ext}$ (mV)')

        kwargs['ax'] = ax_vm
        get_cellvar_timeseries_plot(fname, 'vm', **kwargs)
        ax_vm.set_xlabel('Time (s)')
        ax_vm.set_ylabel('$V_m$ (mV)')

    fig.suptitle(kwargs['title'])

    plt.show()

def plot_waveform_vm(output, waveform, size=(13,7), **kwargs):

    fig, axarr = plt.subplots(2,1, sharex='col', sharey='row', figsize=size)

    kwargs['size'] = None
    kwargs['show_legend'] = False


    (ax_istim, ax_vm) = (axarr[0], axarr[1])

    kwargs['ax'] = ax_vm
    get_cellvar_timeseries_plot(output, 'vm', **kwargs)
    ax_vm.set_xlabel('Time (s)')
    ax_vm.set_ylabel('$V_m$ (mV)')
    xvals = ax_vm.lines[0].get_xdata()

    ax_istim.plot(xvals, [waveform.calculate(x) for x in xvals])
    ax_istim.set_xlabel('Time (s)')
    ax_istim.set_ylabel('$I_{stim}$ (mA)')

    fig.suptitle(kwargs['title'])

    plt.show()

def plot_vm_spikes_raster(output, **kwargs):

    size = (13, 9)

    fig, (ax_vm, ax_spikes) = plt.subplots(2, 1, sharex='col', gridspec_kw={'height_ratios': [5, 1]}, figsize=size)

    ax_vm = get_cellvar_timeseries_plot(output, 'vm', ax=ax_vm, **kwargs)
    ax_vm.set_title('Membrane Voltage')
    ax_vm.set_ylabel('$V_m$ (mV)')
    # ax_vm.set_xlabel('Time (s)')

    kwargs['ax'] = ax_spikes
    ax_spikes = get_spikes_raster_plot(output, **kwargs)
    ax_spikes.set_title('Spikes')

    plt.show()


def plot_spikes_raster(output, size=(10, 1.2), **kwargs):
    kwargs['size'] = size
    ax = get_spikes_raster_plot(output, **kwargs)
    ax.set_title('Spike raster')

    plt.show()


def plot_spikes_barcount(output):
    _cells = np.array([0, 1, 2])
    f_spikes = h5py.File(concat_path(output + 'spikes.h5'), 'r')

    rcells = _cells[::-1]
    plt.figure()
    plt.barh(_cells, map(lambda c: f_spikes[str(c)].value.size, rcells), align='center')
    plt.yticks(_cells, map(lambda c: 'cell_' + str(c), rcells))
    plt.xlabel('Number spikes')
    plt.show()

    f_spikes.close()

def plot_cell_morphology(cell_id, **kwargs):

    ax = get_cell_morphology_plot(cell_id, **kwargs)
    plt.show()

def plot_cell_morphology_tile(cell_ids):
    fig, axarr = plt.subplots(1, len(cell_ids), figsize=(13, 7))

    for i,id in enumerate(cell_ids):
        get_cell_morphology_plot(id, ax=axarr[i])

    plt.show()

