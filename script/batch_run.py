import sys,os
import itertools
from generate_config import *

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

config_file_name = "config.json" # All config files have same name??


#################################################
#
#     RECORD KEEPING
#
#################################################

write_record = False

if write_record:
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

## TEST config
batch_dc_conf = {
    'els'  : range(5),
    'cells': [313862022, 314831019],
    'amps' : [-.01, -.02, -.03]
}

# with open(record_name, "a") as record:
#
#     for combination in itertools.product(*batch_dc_conf.values()):
#
#         (el, cell, amp) = combination
#         trial = 0 # TODO hook this up
#         # print combination, config_base
#
# ## TODO not ready. generate config dir not set and run command not finalized
#         # config_file = generate_config(config_base, config_file_name, dir, el, cell, amp)
#
#     # for config_file in conf_file_names:
#     #
#         print 'Running simulation with ' + config_file_name + ' ' + str(combination)
#         # fp = '/'.join([conf_folder, config_file_name])
#         # run(config_file_name) // hand full path....
#
#         # must've finished... so write to record
#         if write_record:
#             run_id += 1
#             items = [str(run_id), cell, get_dc_key(el, amp), trial, config_file_name] ## TODO ADD DATE
#             record.write(sep.join(items) + '\n')

print '~~ DONE! ~~'








