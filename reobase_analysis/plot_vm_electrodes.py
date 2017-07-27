import matplotlib.pyplot as plt
import reobase_analysis.tchelpers as tc
import reobase_analysis.reobase_utils as ru

# operating params
cell = 313862022
amp = -0.03
electrodes = range(20,41,4)

def plot(cell_gid, amp, els):
    # fetch voltage traces and plot
    plt.figure(figsize=(13,7))
    ax = plt.subplot(111)
    for el in els:
        out = ru.get_dc_output_dir(cell_gid, el, amp)
        tc.get_cellvar_timeseries_plot(out, 'vm', ax=ax, label=str(el))
        plt.legend(title="Electrode #")
        
    ax.set_title('$V_m$ traces for multiple electrodes')
    ax.set_xlabel('$V_m$')
    ax.set_xlabel('Time (s)')
    plt.show()
    
    
plot(cell, amp, electrodes)