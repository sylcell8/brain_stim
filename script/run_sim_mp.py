import argparse
import multiprocessing as mp
import os

"""
Unused.... an idea for a parallel version of the sim runner
"""

# args
parser = argparse.ArgumentParser()
parser.add_argument("run_script", help="location of script to pass config files to")
parser.add_argument("confs_dir", help="dir with set of config files")
# # optional
parser.add_argument("-p", "--processes", help="number of processes to use", default=1, type=int)
# parser.add_argument("-t", "--trial", help="trial number for output folders, default 0", type=int, default=0, action="store_true")
sargs = parser.parse_args()


def walk_paths(confs_dir):
    for root, dirs, files in os.walk(confs_dir):
        for name in files:
            yield os.path.join(root, name)

def run_wrapper(func, *args):
    try:
        return func(*args)
    except Exception as error:
        print error
        return 1

def run_simulation(run_script, config):
    run_args = ['python', run_script, config]
    command = ' '.join(run_args)
    # print command
    return os.system(command)

conf_files = walk_paths(sargs.confs_dir)

pool = mp.Pool(processes=sargs.processes)
results = [pool.apply_async(run_wrapper, args=(run_simulation, sargs.run_script, conf)) for conf in conf_files]
# can also pass callback=callbackfunct, error_callback=handle_error to apply_async
output = [p.get() for p in results]
print(output)