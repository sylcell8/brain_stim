import shutil
import copy
from reobase_utils import *


#
#  For generating batches of config files
#

def generate_config_set(config_base, bconf, confs_folder='confs', verbose=False):
    """ Parse batch config file and enumerate/use all run combinations; run validation checks """

    validate_bconf(bconf) # try to avoid wonky stuff

    cell = bconf['cell_gid']
    el_range = bconf['el_range']
    els = range(el_range[0], el_range[1])
    considerations = [els, bconf['amps']]
    stim_type = bconf['stim_type']
    waveform_type = bconf['stim_type'].split('_')[0]

    # key function used for consistent naming
    key_fn = {
        'dc': get_dc_key,
        'sin': get_sin_key,
    }.get(waveform_type)

    # only add freqs if it's there
    if 'freqs' in bconf:
        considerations += [bconf['freqs']]

    # empty lists will cause empty product below
    for arr in considerations:
        if len(arr) == 0:
            raise ValueError('Cannot pass empty array as value set in for batch config')

    # TODO support SIN waveform
    for combo in itertools.product(*considerations):
        (electrode, amp) = combo
        el_filled = format_el(electrode)
        conf_name = 'config_{}.json'.format(key_fn(el_filled, amp))
        conf_data = generate_config(config_base, conf_name, confs_folder, el_filled, cell, amp,
                                    trial=bconf['trial'], stim_type=stim_type)

        if verbose:
            print 'KEY: ', key_fn(*combo), '   -----   OUTPUT DIR: ', conf_data["manifest"]["$OUTPUT_DIR"]


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

    return data

def validate_bconf(bconf):

    must_haves = {'el_range':list, 'cell_gid':int, 'amps':list, 'trial':int, 'stim_type':str}

    for name, t in must_haves.iteritems():
        if name not in bconf:
            raise ValueError("You are required to include '{}' in the batch configuration".format(name))

        if name == 'cell_gid':
            if not bconf[name].isdigit():
                raise ValueError("Invalid cell_gid {}".format(bconf[name]))
        elif type(bconf[name]) != t:
            raise ValueError("Invalid type for '{}' ({})".format(name, type(bconf[name])))

    waveform_type = bconf['stim_type'].split('_')[0]

    if waveform_type == 'dc':
        if 'freqs' in bconf:
            raise ValueError("Cannot include 'freqs' key in batch config when using DC input")
    elif waveform_type == 'sin':
        if 'freqs' not in bconf:
            raise ValueError("Must include 'freqs' list in batch config when using sin input")
    else:
        print 'Cannot validate unknown waveform type {} --I suggest implementing some common sense checks'.format(waveform_type)

# "Reset" a folder - would make a good general util
def prep_confs_folder(confs_folder):
    if os.path.isdir(confs_folder):
        # clear it
        shutil.rmtree(confs_folder)

    os.mkdir(confs_folder) # placed in current dir

