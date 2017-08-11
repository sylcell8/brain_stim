import shutil
import copy
from reobase_utils import *


#
#  For generating batches of config files
#

def generate_config_set(config_base, bconf, confs_folder='confs', verbose=False):
    """ Parse batch config file and enumerate all run combinations; run checks """
    cell = bconf['cell_gid']
    el_range = bconf['el_range']
    els = range(el_range[0], el_range[1])
    considerations = [els, bconf['amps']]
    stim_type = bconf['stim_type'] ## TODO run safety checks based on stim type


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
        generate_config(config_base, conf_name, confs_folder, el_filled, cell, amp,
                        trial=bconf['trial'], stim_type=stim_type)


def set_config(conf_data, el, cell, amp, trial=0, stim_type='dc'):
    """ Lots of config settings are cell specific or input specific--all changes to the conf file should go here """
    el = format_el(el) ## TODO stop being weird about el... call the string filled_el or use a number
    cell = str(cell)
    run_folder = get_dc_dir_name(el, amp, trial)

    conf_data["extracellular_stimelectrode"]["position"] = "$STIM_DIR/" + cell + "_" + el + ".csv"
    conf_data["extracellular_stimelectrode"]["waveform"]["amp"] = amp
    # Note: output dir doesn't include current sign
    outdir_root = conf_data["manifest"]["$OUTPUT_DIR"]
    conf_data["manifest"]["$OUTPUT_DIR"] = concat_path(outdir_root, stim_type, cell, run_folder)
    conf_data["manifest"]["$STIM_DIR"]   = concat_path("$BASE_DIR/stimulation", cell)
    # single cell definition and per-cell connection functions
    conf_data["internal"]["cells"]     = "$NETWORK_DIR/{}_cell.csv".format(cell)
    conf_data["internal"]["con_types"] = "$NETWORK_DIR/{}_func.csv".format(cell)

    return conf_data

def generate_config(base, filename, out_dir, el_filled, *args, **kwargs):
    """ Per file logic -- modify base config data and then store in new file """
    with open(base, 'r') as fp:
        base_data = json.load(fp)

    data = set_config(copy.deepcopy(base_data), el_filled, *args, **kwargs)

    with open(out_dir + '/' + filename, 'w') as fp:
        json.dump(data, fp, indent=4, separators=(',', ': ')) # print pretty

    return filename

def validate_bconf(bconf):
    stim_type = bconf['stim_type']
    stim_parts = stim_type.split('_')
    waveform_type = stim_parts[0]

    if waveform_type == 'dc':
        pass
    elif waveform_type == 'sin':
        pass
    else:
        print 'Cannot validate unknown waveform type {} --I suggest implementing some common sense checks'.format(waveform_type)

# "Reset" a folder - would make a good general util
def prep_confs_folder(confs_folder):
    if os.path.isdir(confs_folder):
        # clear it
        shutil.rmtree(confs_folder)

    os.mkdir(confs_folder) # placed in current dir

