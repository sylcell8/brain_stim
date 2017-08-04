import shutil
import copy
import itertools
from reobase_utils import *


#
#  For generating batches of config files
#


def set_config(conf_data, el, cell, amp, trial=0, stim_type='dc'):
    el = format_el(el)
    cell = str(cell)
    run_folder = get_dc_dir_name(el, amp, trial)

    conf_data["extracellular_stimelectrode"]["position"] = "$STIM_DIR/" + cell + "_" + el + ".csv"
    conf_data["extracellular_stimelectrode"]["waveform"]["amp"] = amp
    # Note: output dir doesn't include current sign
    user_defined_outdir = conf_data["manifest"]["$OUTPUT_DIR"]	
    conf_data["manifest"]["$OUTPUT_DIR"] = "/".join([ user_defined_outdir, stim_type, cell, run_folder])
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

def prep_confs_folder(confs_folder):
    if os.path.isdir(confs_folder):
        # clear it
        shutil.rmtree(confs_folder)

    os.mkdir(confs_folder) # placed in current dir

def generate_config_set(config_base, bconf, confs_folder='confs', verbose=False):
    cell = bconf['cell_gid']
    el_range = bconf['el_range']
    els = range(el_range[0], el_range[1])
    considerations = [els, bconf['amps']]

    # only add freqs if it's there
    if 'freqs' in bconf:
        print "Set of frequencies passed in config -- be sure you are using a sin waveform! (otherwise you will get many duplicates)"
        considerations += bconf['freqs']

    for arr in considerations:
        if len(arr) == 0:
            raise ValueError('Cannot pass empty array as value set in for batch config')

    for combo in itertools.product(*considerations):
        if verbose:
            print get_dc_key(*combo)

        # print combo, considerations, els, bconf
        (electrode, amp) = combo
        el_filled = format_el(electrode)
        conf_name = 'config_{}.json'.format(get_dc_key(el_filled, amp))
        generate_config(config_base, conf_name, confs_folder, el_filled, cell, amp, bconf['trial'])
