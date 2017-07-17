import sys,os
import json
import math
import shutil
import copy

sys_args = list(sys.argv) # command line arguments

config_base = str(sys_args[1]) # default values for config
number_el = int(sys_args[2])   # number of electrode position files you wish to use
cell_gid = int(sys_args[3])

confs_folder = 'confs'

#################################################
#
#     Functions
#
#################################################

def get_dc_key(elnum_filled, amp):
    parts = ['el' + elnum_filled, "amp{0:.0f}".format(math.fabs(amp * 1000.))]
    return '_'.join(parts)

def dc_folder_format(key, trial=0):
    parts = [key, 'tr' + str(trial)]
    return '_'.join(parts)

def set_config(conf_data, el_filled, cell_gid, amp, stim_type='dc'):
    cell_gid = str(cell_gid)
    run_folder = dc_folder_format(get_dc_key(el_filled, amp)) # TODO all trials are 0 eh??
    print run_folder

    conf_data["extracellular_stimelectrode"]["position"] = "$STIM_DIR/" + cell_gid + "_" + str(el) + ".csv"
    conf_data["extracellular_stimelectrode"]["waveform"]["amp"] = amp
    # Note: output dir doesn't include current sign
    conf_data["manifest"]["$OUTPUT_DIR"] = "/".join([ "$RUN_DIR/outputs", stim_type, cell_gid, run_folder])

    return conf_data

def generate_config(config_base, file_name_tpl, dir, el, *args):
    with open(config_base, 'r') as fp:
        base_data = json.load(fp)


    el_filled = str(el).zfill(4)
    data = set_config(copy.deepcopy(base_data), el_filled, *args)

    filename = file_name_tpl.format(el_filled)

    with open(dir + '/' + filename, 'w') as fp:
        json.dump(data, fp, indent=4, separators=(',', ': ')) # print pretty

    return filename

#################################################
#
#     Generate set of files in ./confs_folder
#
#################################################


with open(config_base, 'r') as fp:
    data = json.load(fp)

# current gotten from config base -- given in milliamps ... float(args[3]) if len(args) > 30000 else
current = data["extracellular_stimelectrode"]["waveform"]["amp"]
print 'Using current amplitude from base config:' + str(current)

if os.path.isdir(confs_folder):
    # clear it
    shutil.rmtree(confs_folder)

os.mkdir(confs_folder) # placed in current dir

for el in range(number_el):
    generate_config(config_base, 'config_el{}.json', confs_folder, el, cell_gid, current)

print '~~ DONE! ~~'
