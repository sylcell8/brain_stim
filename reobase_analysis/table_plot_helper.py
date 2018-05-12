import numpy as np
import pandas as pd
import matplotlib as mlb
import matplotlib.pyplot as plt
import reobase_analysis.reobase_utils as ru
from matplotlib.mlab import griddata
import h5py


def get_grouped_dic(cell_list, input_type, stim_type, model_type, amp_range, trial, groupby_cols, agg_cols):
    data = {}
    for cell_id in cell_list:
        table = ru.read_cell_tables(input_type=input_type, stim_type=stim_type, model_type=model_type,
                                    cell_gid=cell_id, amp_range=amp_range, trial=trial)
        print "finished reading the table for cell_id:", cell_id
        # index_close_els = ru.get_index_close_els(cell_id, input_type, stim_type, model_type)
        # table = table.drop(index_close_els)
        print "Turned Vm_phase to vm_phase +360"
        table.loc[table["vm_phase"] < 0, "vm_phase"] = table["vm_phase"] + 360

        data[cell_id] = table.groupby(groupby_cols)[agg_cols].mean().reset_index()
    return data


def get_merged_table(dic, merge_cols):
    dfs = [v for k, v in dic.iteritems()]
    merged = reduce(lambda left, right: pd.merge(left, right, on=merge_cols, how='outer'), dfs)
    return merged


def get_agg_merged_colnames(merged_table, var_name):

    var_agg_merged_colname = np.unique([col for col in merged_table.columns if var_name in col]).tolist()
    return var_agg_merged_colname


def get_stdcol_3d_colorbar(merged_table, var_name):
    col = var_name
    agg_merged_colnames = get_agg_merged_colnames(merged_table, var_name)
    std_col = merged_table[agg_merged_colnames].std(axis=1).as_matrix()
    n_sample = len(std_col)
    std_col = std_col/np.sqrt(n_sample)
    return std_col

def get_meancol_3d_colorbar(merged_table, var_name):
    col = var_name
    agg_merged_colnames = get_agg_merged_colnames(merged_table, var_name)
    mean_col = merged_table[agg_merged_colnames].mean(axis=1).as_matrix()
    return mean_col


def get_mesh_X_Y_Z_Z1(merged_table, xcol, zcol, z1col, ycol="distance", error=False):
    
    x = get_meancol_3d_colorbar(merged_table, xcol)
    z = get_meancol_3d_colorbar(merged_table, zcol)
    z1 = get_meancol_3d_colorbar(merged_table, z1col)
    if error:
        print "error"
        x = get_meancol_3d_colorbar(merged_table, xcol)
        z = get_stdcol_3d_colorbar(merged_table, zcol)
        z1 = get_stdcol_3d_colorbar(merged_table, z1col)

    y = merged_table["distance"].as_matrix()

    xi = np.linspace(np.min(x), np.max(x))
    yi = np.linspace(np.min(y), np.max(y))

    X, Y = np.meshgrid(xi, yi)
    Z = griddata(x, y, z, xi, yi, interp='linear')
    Z1 = griddata(x, y, z1, xi, yi, interp='linear')
    return X, Y, Z, Z1


def plot_mediancol1_col2(gids_list, colname1, colname2, amp, stim_type, model_type, trial):
    med_dic = {}
    d_list = []

    for gid in gids_list:
        t = ru.read_cell_tables(gid, [amp], stim_type, model_type, trial)
        groups = t.groupby([colname2])

        med = []
        for d, g in groups:
            d_list = d_list + [d]
            med.append(g[colname1].agg(np.median, axis=0))

        med_dic[gid] = med

    box_data = [[med_dic[gid][i] for gid in gids_list] for i in range(len(groups))]
    filtered_data = []

    for list in box_data:
        filtered_data.append([x for x in list if ~np.isnan(x)])

    fig = plt.figure()
    fig.set_figheight(7)
    fig.set_figwidth(15)
    ax = fig.add_subplot(111)

    if colname1 == "delta_vm":
        ax.set_title('Median of $\Delta$Vm distribution by distance (amp = {})'.format(amp), fontsize=15)
        ax.set_ylabel('$\Delta$Vm (mV)', fontsize=20)
    else:
        ax.set_title('Median of spike frequency distribution by distance (amp = {})'.format(amp), fontsize=15)
        ax.set_ylabel('Spike frequency (Hz)', fontsize=20)

    ax.set_xlabel('Distance ($\mu$)', fontsize=20)
    boxprops = dict(linewidth=1.5)
    medianprops = dict(linestyle='-', linewidth=1.5, color='firebrick')
    ax.tick_params(labelsize=15)
    ax.boxplot(filtered_data, showmeans=True, boxprops=boxprops, medianprops=medianprops)
    ax.set_xticklabels(["{0:4.2f}".format(x) for x in d_list])
    Fig_folder="/allen/aibs/mat/Fahimehb/Data_cube/reobase/Run_folder/result_figures/dc/progress_report_figs/"
    Fig_name = "Fig.png"
    plt.savefig(Fig_folder + Fig_name)

    plt.show()


def groupby_plot(table, groupby_col, plotx, ploty):
    for groupcol, group in table.groupby(groupby_col):
        fig, ax = plt.subplots()
        ax.plot(group[plotx], group[ploty], marker='o', linestyle='', ms=10)
        ax.set_xlabel(plotx)
        ax.set_ylabel(ploty)
        ax.set_title('{}=  {}'.format(groupby_col, groupcol))
        ax.set_xlim([0,110])
    plt.show()


def passive_comparison(table_pass_peri, table_pass_aa, amp):
    fig, ((ax1, ax2)) = plt.subplots(1, 2, sharex=False, sharey=False)
    fig.set_figheight(5)
    fig.set_figwidth(15)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, hspace=None)

    ax1.plot(table_pass_peri[table_pass_peri["amp"] == amp]["electrode"],
             table_pass_peri[table_pass_peri["amp"] == amp]["delta_deltav"])
    ax2.plot(table_pass_aa[(table_pass_aa["delta_deltav"] <20) & (table_pass_aa["amp"] == amp)]["electrode"],
             table_pass_aa[(table_pass_aa["delta_deltav"] <20) & (table_pass_aa["amp"] == amp)]["delta_deltav"])

    ax1.set_xlabel("electrode_id", size=15)
    ax2.set_xlabel("electrode_id", size=15)
    ax1.set_ylabel("delta_deltav (mV)", size=15)

    ax1.set_title('{}, amp = {}'.format("perisomatic", amp), size=15)
    ax2.set_title('{}, amp = {}'.format("all_active", amp), size=15)
    plt.show()


def Build_subthreshold_comparison_table(gid, Model_Type, Stim_Type, list_trials, inputs):

        table_temp = {}
        table_pass_peri = pd.DataFrame()
        for tr in list_trials:
            table_temp[tr] = ru.read_cell_tables(gid, inputs ,Stim_Type, Model_Type, trial=tr)
            new_deltavm = "delta_vm" + str(tr)
            table_temp[tr] = table_temp[tr].rename(columns={'delta_vm': new_deltavm})
            table_temp[tr]["distance"] = table_temp[tr]["distance"].round()

        table_pass_peri = pd.merge(table_temp[list_trials[0]][["electrode", "x", "y", "z", "distance", "amp", "delta_vm" + str(list_trials[0])]],
                                   table_temp[list_trials[1]][["electrode", "x", "y", "z", "distance", "amp", "delta_vm" + str(list_trials[1]) ]],
                                   on=["electrode", "amp", "x", "y", "z", "distance"]).sort_values(by=["electrode"])
        table_pass_peri["delta_deltav"] = table_pass_peri["delta_vm" + str(list_trials[0])] - table_pass_peri["delta_vm" + str(list_trials[1])]
        # table_pass_peri["avg_deltav"] = (table_pass_peri["delta_vm0"] + table_pass_peri["delta_vm1"]) / 2.
        return table_pass_peri

##################################################
#                                                #
#                 SIN_DC plots                   #
#                                                #
##################################################

def plot_vm_phase_els_Iclamp(table, ic_amp, fq_range):
    fig = plt.figure(figsize=(20,8))
    for fq in fq_range:
        df = table[(table["ic_amp"]==ic_amp) & (table["fq"]==fq)]
        plt.plot(df["electrode"],df["vm_phase"], marker='o', label="vm_fq={}".format(fq))

    plt.title("Vm and Vext phase as a function of el_id for different frequencies at Iclamp={}pA".format(ic_amp*1000), fontsize=20)
    plt.plot(df["electrode"],df["vext_phase"], label="Vext")
    plt.xlabel("Electrode id", fontsize=20)
    plt.ylabel("Phase (degree)", fontsize=20)
    plt.legend(fontsize=15)
    plt.show()


def plot_vm_phase_els_freq(table, ic_amp_range, freq):

    fig = plt.figure(figsize=(20,8))
    for icamp in ic_amp_range:
        df = table[(table["ic_amp"]==icamp) & (table["fq"]==freq)]
        plt.plot(df["electrode"],df["vm_phase"], marker='o', label="vm_icamp={}".format(icamp))

    plt.title("Vm and Vext phase as a function of el_id for different Iclamp at fq={}".format(freq), fontsize=20)
    plt.plot(df["electrode"],df["vext_phase"], label="Vext")
    plt.xlabel("Electrode id", fontsize=20)
    plt.ylabel("Phase (degree)", fontsize=20)
    plt.legend(fontsize=15)
    plt.show()

def plot_vm_amplitude_els_Iclamp(table, ic_amp, fq_range):
    fig = plt.figure(figsize=(20,8))
    for fq in fq_range:
        df = table[(table["ic_amp"]==ic_amp) & (table["fq"]==fq)]
        plt.plot(df["electrode"],df["vm_amp"], marker='o', label="vm_fq={}".format(fq))

    plt.title("Vm and Vext amplitude as a function of el_id for different frequencies at Iclamp={}pA".format(ic_amp*1000), fontsize=20)
    plt.plot(df["electrode"],df["vext_amp"], label="Vext")
    plt.xlabel("Electrode id", fontsize=20)
    plt.ylabel("Amplitude (mV)", fontsize=20)
    plt.legend(fontsize=15)
    plt.show()

def plot_vm_amplitude_els_freq(table, ic_amp_range, freq):

    fig = plt.figure(figsize=(20,8))
    for icamp in ic_amp_range:
        df = table[(table["ic_amp"]==icamp) & (table["fq"]==freq)]
        plt.plot(df["electrode"],df["vm_amp"], marker='o', label="vm_icamp={}".format(icamp))

    plt.title("Vm and Vext amplitude as a function of el_id for different Iclamp at fq={}".format(freq), fontsize=20)
    plt.plot(df["electrode"],df["vext_amp"], label="Vext")
    plt.xlabel("Electrode id", fontsize=20)
    plt.ylabel("Amplitude (mV)", fontsize=20)
    plt.legend(fontsize=15)
    plt.show()
