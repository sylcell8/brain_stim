import numpy as np
import pandas as pd
import matplotlib as mlb
import matplotlib.pyplot as plt
import reobase_analysis.reobase_utils as ru
import h5py


def groupby_plot(table, groupby_col, plotx, ploty):
    for groupcol, group in table.groupby(groupby_col):
        fig, ax = plt.subplots()
        ax.plot(group[plotx], group[ploty], marker='o', linestyle='', ms=10)
        ax.set_xlabel(plotx)
        ax.set_ylabel(ploty)
        ax.set_title('{}=  {}'.format(groupby_col, groupcol))
        ax.set_xlim([0,110])
    # plt.show()


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


def build_perisomatic_assess_table(gid, list_trials, inputs):

        table_temp = {}
        table_pass_peri = pd.DataFrame()
        for tr in list_trials:
            table_temp[tr] = ru.read_cell_tables(gid, inputs, "dc", "passive", trial=tr)
            new_deltavm = "delta_vm" + str(tr)
            table_temp[tr] = table_temp[tr].rename(columns={'delta_vm': new_deltavm})
            table_temp[tr]["distance"] = table_temp[tr]["distance"].round()

        table_pass_peri = pd.merge(table_temp[0][["electrode", "x", "y", "z", "distance", "amp", "delta_vm0"]],
                                   table_temp[1][["electrode", "x", "y", "z", "distance", "amp", "delta_vm1"]],
                                   on=["electrode", "amp", "x", "y", "z", "distance"]).sort_values(by=["electrode"])
        table_pass_peri["delta_deltav"] = table_pass_peri["delta_vm0"] - table_pass_peri["delta_vm1"]
        table_pass_peri["avg_deltav"] = (table_pass_peri["delta_vm0"] + table_pass_peri["delta_vm1"]) / 2.
        return table_pass_peri


def build_allactive_assess_table(gid, list_trials, inputs):
    table_temp = {}
    table_pass_aa = pd.DataFrame()
    for tr in list_trials:
        table_temp[tr] = ru.read_cell_tables(gid, inputs, "dc", "passive", trial=tr)
        new_deltavm = "delta_vm" + str(tr)
        table_temp[tr] = table_temp[tr].rename(columns={'delta_vm': new_deltavm})
        table_temp[tr]["distance"] = table_temp[tr]["distance"].round()

    table_pass_aa = pd.merge(table_temp[2][["electrode", "x", "y", "z", "distance", "amp", "delta_vm2"]],
                               table_temp[3][["electrode", "x", "y", "z", "distance", "amp", "delta_vm3"]],
                               on=["electrode", "amp", "x", "y", "z", "distance"]).sort_values(by=["electrode"])
    table_pass_aa["delta_deltav"] = table_pass_aa["delta_vm2"] - table_pass_aa["delta_vm3"]
    table_pass_aa["avg_deltav"] = (table_pass_aa["delta_vm2"] + table_pass_aa["delta_vm3"]) / 2.
    return table_pass_aa