#python run_reobase.py config_test.json 5 55 10 1800 10
import sys,os
import isee_engine.bionet.config as config
import isee_engine.bionet.stimxreobase as reobase
import argparse


# args
parser = argparse.ArgumentParser()
parser.add_argument("config_file", help="config file to use as template")
parser.add_argument("rmin", help="starting distance to put electrodes", type=int)
parser.add_argument("rmax", help="longest distance to put electrodes")
parser.add_argument("rstep", help="the step for r")
parser.add_argument("Npoints", help="total number of points to put")
parser.add_argument("min_dist_tocell", help="remove all the points closer than this value")


sargs = parser.parse_args()

config_file = sargs.config_file

rmin = sargs.rmin

rmax = sargs.rmax

rstep = sargs.rstep

Npoints = sargs.Npoints

min_dist_tocell = sargs.min_dist_tocell

conf = config.build(config_file) # Read all the pathes from the manifest 

electrode = reobase.MeshXElectrode(conf, rmin, rmax, rstep, Npoints, min_dist_tocell)

electrode.mkdir_reobase_electrode_folder()

electrode.read_swc_list()

electrode.make_mesh_soma()

