import matplotlib.pyplot as plt
import numpy as np
import reobase_analysis.tchelpers as tc
import reobase_analysis.reobase_utils as ru

#%% Compare different electrodes
def plot_els(cell_gid, amp, els, trial=0):
    plt.figure(figsize=(13,7))
    ax = plt.subplot(111)
    # fetch voltage traces and plot
    for el in els:
        out = ru.get_dc_output_dir(cell_gid, el, amp, trial=trial)
        electrodes_dir = ru.concat_path(out,'electrodes')
        pos = ru.get_electrode_xyz(ru.get_electrode_path(electrodes_dir, cell_gid, el))
        dist = np.linalg.norm(pos[0])
        tc.get_cellvar_timeseries_plot(out, 'vm', ax=ax, label=str(dist))
        plt.legend(loc='upper left', title="Distance")
        
    ax.set_title('$V_m$ traces when cell was stimulated with point-source electrodes and $I_{stim}$ = '+'{}'.format(amp))
    ax.set_ylabel('$V_m$ (mV)')
    ax.set_xlabel('Time (s)')
    plt.show()
    
    
print "Try running: 'plot(313862022, -0.03, range(20,41,4))'"

plot_els(313862022, -0.06, range(400,410))
#plot_els(313862022, -0.03, [100,300])


#%% Compare different amplitudes
def plot_amps(cell_gid, amps, el, trial=0):
    plt.figure(figsize=(13, 7))
    ax = plt.subplot(111)
    dist = None
    # fetch voltage traces and plot
    for amp in amps:
        out = ru.get_dc_output_dir(cell_gid, el, amp, trial=trial)
        electrodes_dir = ru.concat_path(out, 'electrodes')
        pos = ru.get_electrode_xyz(ru.get_electrode_path(electrodes_dir, cell_gid, el))
        dist = np.linalg.norm(pos[0]) # should always be the same, just need one
        tc.get_cellvar_timeseries_plot(out, 'vm', ax=ax, label=str(amp))
        plt.legend(loc='upper left', title="$I_{stim}$")

    ax.set_title(
        '$V_m$ traces when cell was stimulated with point-source electrodes and distance = ' + '{}'.format(dist))
    ax.set_ylabel('$V_m$ (mV)')
    ax.set_xlabel('Time (s)')
    plt.show()
    
plot_amps(313862022, [-0.02, -0.06], 400)

#%% Compare across trials


#plt.figure(figsize=(13,7))
#ax = plt.subplot(111)
#for t in [0,1]:
#    out = ru.get_dc_output_dir(313862022, 60, -0.03, trial=t)
#    tc.get_cellvar_timeseries_plot(out, 'vm', ax=ax)
#    
#ax.set_title('$V_m$ traces when cell was stimulated with point-source electrodes and $I_{stim}$ = '+'{}'.format('amp'))
#ax.set_ylabel('$V_m$ (mV)')
#ax.set_xlabel('Time (s)')
#plt.show()