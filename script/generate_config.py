import argparse
from reobase_analysis.generate_utils import *

# args
parser = argparse.ArgumentParser()
parser.add_argument("config_base", help="config file to use as template")
parser.add_argument("number_el", help="number of electrodes to use, from 0 to number_el", type=int)
parser.add_argument("cell_gid", help="cell gid for all config files")
# optional
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-t", "--trial", help="trial number for output folders, default 0", type=int, default=0)
sargs = parser.parse_args()

confs_folder = 'confs'
config_base = sargs.config_base
batch_config = {
    "el_range": [0, sargs.number_el],
    "cell_gid": sargs.cell_gid,
    "amps": [-0.01, -0.02, -0.03],
    # "freqs": [10, 40, 70],
    "trial": sargs.trial,
    "stim_type":'dc_lgn_poisson', # output directory name -- differs from waveform type, b/c includes external inputs
}

print sargs



#################################################
#
# Generate set of files according to batch_config
#
#################################################

print 'Using current amplitude(s): {}'.format(batch_config['amps'])

if 'freqs' in batch_config:
    print 'Using frequencies: {}'.format(batch_config['freqs'])

prep_confs_folder(confs_folder)
generate_config_set(config_base, batch_config, confs_folder, verbose=sargs.verbose)

print '~~ Done! ~~'
