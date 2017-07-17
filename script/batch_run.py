import sys,os
import math
import json
import copy

import itertools

from run_sim import run

# print os.getcwd()
sys_args = list(sys.argv) # get config file name from the command line argument
config_base = str(sys_args[1])
# conf_folder = str(sys_args[1]) if len(sys_args) > 1 else 'confs'
# conf_file_names = os.listdir(conf_folder) # a folder of conf files

#################################################
#
#     GENERATE CONFIG
#
#################################################

config_file_name = "config.json" # All config files have same name

def get_dc_key(elnum_filled, amp):
    parts = ['el' + elnum_filled, "amp{0:.0f}".format(math.fabs(amp * 1000.))]
    return '_'.join(parts)

def dc_folder_format(key, trial=0):
    parts = [key, 'tr' + str(trial)]
    return '_'.join(parts)

def set_config(conf_data, el, cell_gid, amp, stim_type='dc'):
    cell_gid = str(cell_gid)
    elnum_filled = str(el).zfill(3)
    run_folder = dc_folder_format(get_dc_key(elnum_filled, amp)) # TODO all trials are 0 eh??
    print run_folder

    # file_name = "config_file_el" + elnum_filled + ".json"
    conf_data["extracellular_stimelectrode"]["position"] = "$STIM_DIR/" + cell_gid + "_" + str(el) + ".csv"
    conf_data["extracellular_stimelectrode"]["waveform"]["amp"] = amp
    # Note: output dir doesn't include current sign
    conf_data["manifest"]["$OUTPUT_DIR"] = "/".join([ "$RUN_DIR/output", stim_type, cell_gid, run_folder])

    return conf_data

def generate_config(config_base, *args):
    with open(config_base, 'r') as fp:
        base_data = json.load(fp)

    # For whatever conditions
    data = set_config(copy.deepcopy(base_data), *args)

    with open(config_file_name, 'w') as fp:
        json.dump(data, fp, indent=4, separators=(',', ': ')) # print pretty

    return config_file_name # TODO this doesn't make sense the moment


#################################################
#
#     RECORD KEEPING
#
#################################################

record_name = "run_record.csv"
# folder will be key + trial--"key" is meant to denote is as a unique identifier under a particular stimulation type
headers = ['id', 'cell', 'key', 'trial', 'config']
sep = ' '
run_id = -1

if os.path.exists(record_name):
    # find out last run id from record -> increment and go
    last_line = os.popen("tail -n 1 %s" % record_name).read()
    run_id = int(last_line.split(sep)[0])
    print 'Record found, with last run id: {}'.format(run_id)
else:
    with open(record_name, "w") as record:
        record.writelines(sep.join(headers) + '\n')
    print 'No record found: starting new record'


#################################################
#
#     RUN SIMULATION
#
#################################################

batch_dc_conf = {
    'els'  : range(5),
    'cells': [313862022, 314831019],
    'amps' : [-.01, -.02, -.03]
}

with open(record_name, "a") as record:

    for combination in itertools.product(*batch_dc_conf.values()):

        (el, cell, amp) = combination
        trial = 0 # TODO hook this up
        # print combination, config_base

        config_file = generate_config(config_base, el, cell, amp)

    # for config_file in conf_file_names:
    #
        print 'Running simulation with ' + config_file + ' ' + str(combination)
        # fp = '/'.join([conf_folder, config_file])
        # run(config_file)

        # must've finished... so write to record
        run_id += 1
        items = [str(run_id), cell, get_dc_key(el, amp), trial, config_file]
        record.write(sep.join(items) + '\n')

print '~~ DONE! ~~'








