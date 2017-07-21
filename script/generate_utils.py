import sys,os
import json
import math
import shutil
import copy

import itertools


def get_dc_key(el, amp):
    parts = ['el' + fill_el(el), "amp{0:.0f}".format(math.fabs(amp * 1000.))]
    return '_'.join(parts)

def dc_folder_format(key, trial):
    parts = [key, 'tr' + str(trial)]
    return '_'.join(parts)

def set_config(conf_data, el, cell, amp, trial=0, stim_type='dc'):
    el = fill_el(el)
    cell = str(cell)
    run_folder = dc_folder_format(get_dc_key(el, amp), trial)

    conf_data["extracellular_stimelectrode"]["position"] = "$STIM_DIR/" + cell + "_" + el + ".csv"
    conf_data["extracellular_stimelectrode"]["waveform"]["amp"] = amp
    # Note: output dir doesn't include current sign
    conf_data["manifest"]["$OUTPUT_DIR"] = "/".join([ "$RUN_DIR/outputs", stim_type, cell, run_folder])
    conf_data["manifest"]["$STIM_DIR"] = "/".join([ "$BASE_DIR/stimulation", cell])

    return conf_data

def generate_config(base, file_name_tpl, out_dir, el_filled, *args):
    with open(base, 'r') as fp:
        base_data = json.load(fp)


    data = set_config(copy.deepcopy(base_data), el_filled, *args)

    filename = file_name_tpl.format(el_filled)

    with open(out_dir + '/' + filename, 'w') as fp:
        json.dump(data, fp, indent=4, separators=(',', ': ')) # print pretty

    return filename

def fill_el(el): #idempotent
    return str(el).zfill(4)

def prep_confs_folder(confs_folder):
    if os.path.isdir(confs_folder):
        # clear it
        shutil.rmtree(confs_folder)

    os.mkdir(confs_folder) # placed in current dir

def generate_config_set(config_base, bconf, confs_folder='confs', verbose=False):
    cell = bconf['cell_gid']
    el_range = bconf['el_range']
    els = xrange(el_range[0], el_range[1])

    for combination in itertools.product(els, bconf['amps']):
        if verbose:
            print get_dc_key(*combination)

        (electrode, amp) = combination
        el_filled = fill_el(electrode)
        conf_name = 'config_{}.json'.format(get_dc_key(el_filled, amp))
        generate_config(config_base, conf_name, confs_folder, el_filled, cell, amp, bconf['trial'])