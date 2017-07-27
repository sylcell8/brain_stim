import matplotlib.pyplot as plt
import numpy as np
import reobase_analysis.tchelpers as tc
import reobase_analysis.reobase_utils as ru

#%% Plot

def plot(cell_gid, amp, els):
    # fetch voltage traces and plot
    plt.figure(figsize=(13,7))
    ax = plt.subplot(111)
    for el in els:
        out = ru.get_dc_output_dir(cell_gid, el, amp)
        electrodes_dir = ru.concat_path(out,'electrodes')
        pos = ru.get_electrode_xyz(ru.get_electrode_path(electrodes_dir, cell_gid, el))
        dist = np.linalg.norm(pos[0])
        tc.get_cellvar_timeseries_plot(out, 'vm', ax=ax, label=str(dist))
        plt.legend(title="Distance")
        
    ax.set_title('$V_m$ traces when cell was stimulated with point-source electrodes and $I_{stim}$ = '+'{}'.format(amp))
    ax.set_ylabel('$V_m$ (mV)')
    ax.set_xlabel('Time (s)')
    plt.show()
    
    
print "Try running: 'plot(313862022, -0.03, range(20,41,4))'"

#plot(313862022, -0.03, [60])
#plot(313862022, -0.03, [100,300])