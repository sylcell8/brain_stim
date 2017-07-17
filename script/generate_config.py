import json
import math
import sys,os

args = list(sys.argv) # get config file name from the command line argument

config_file = str(args[1])
number_el = int(args[2])
outdir = str(args[3])

if outdir[-1] != '/':
    outdir += '/'

with open(config_file, 'r') as fp:
    data = json.load(fp)

# current optional, given in milliamps
# float(args[3]) if len(args) > 30000 else 
current = data["extracellular_stimelectrode"]["waveform"]["amp"]
print 'using current amplitude ' + str(current)

confs_folder = 'confs'
os.mkdir(confs_folder) # placed in current dir

for el in range(number_el):
    elnum_filled = str(el).zfill(3)
    file_name = "config_file_el" + elnum_filled + ".json"
    data["extracellular_stimelectrode"]["position"] = "$STIM_DIR/313862022_" + str(el) + ".csv"
    data["extracellular_stimelectrode"]["waveform"]["amp"] = current
    # output dir doesn't include current sign --> use conf file for current amp not filename
    data["manifest"]["$OUTPUT_DIR"] = "$RUN_DIR/" + outdir + "{0:.0f}".format(math.fabs(current*1000.)) + "muA_" + elnum_filled
    with open('/'.join([confs_folder, file_name]), 'w') as fp:
        json.dump(data, fp, indent=4, separators=(',', ': ')) # print pretty

print 'done'