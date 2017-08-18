import argparse
from reobase_analysis.build_table import *

# args
parser = argparse.ArgumentParser()
parser.add_argument("cell_gid", help="cell gid, e.g. {}".format(default_gid), type=int)
parser.add_argument("stim_type", help="stimulus type, e.g. 'dc', 'dc_lgn_poisson'")
# optional
parser.add_argument("-i", "--inputs", help="input values. may provide many. may use normal or display form for values, e.g. -0.06 == 60", default=default_inputs,nargs='+', type=float)
parser.add_argument("-t", "--trial", help="trial number for output folders, default 0", type=int, default=0)
sargs = parser.parse_args()

inputs = sargs.inputs

# Deal with input format
if np.abs(int(inputs[0])) == inputs[0]:
    # assume in display form
    inputs = [-1 * i/1000 for i in inputs]

# Validate stim type
if sargs.stim_type not in [e.value for e in StimType]:
    raise ValueError('Invalid stim type provided (be sure type has been added to StimType class)')

# Run it!
build(sargs.cell_gid, inputs, sargs.stim_type, sargs.trial)