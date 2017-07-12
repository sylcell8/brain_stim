import json
import math
import sys,os

args = list(sys.argv) # get config file name from the command line argument

config_file = str(args[1])
number_el = int(args[2])

with open(config_file, 'r') as fp:
    data = json.load(fp)

# current optional, given in milliamps
current = float(args[3]) if len(args) > 3 else data["extracellular_stimelectrode"]["waveform"]["amp"]
print 'using current amplitude ' + str(current)

for el in range(number_el):
    elnum_filled = str(el).zfill(3)
    file_name = "config_file_el" + elnum_filled + ".json"
    data["extracellular_stimelectrode"]["position"] = "$STIM_DIR/313862022_" + str(el) + ".csv"
    data["extracellular_stimelectrode"]["waveform"]["amp"] = current
    # output dir doesn't include current sign --> use conf file for current amp not filename
    data["manifest"]["$OUTPUT_DIR"] = "$RUN_DIR/" + "{0:.0f}".format(math.fabs(current*1000.)) + "muA_" + elnum_filled
    with open(file_name, 'w') as fp:
        json.dump(data, fp, indent=4, separators=(',', ': ')) # print pretty

print 'done'