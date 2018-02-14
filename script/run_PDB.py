#python /home/fahimehb/Pycode/Brain_stim/script/run_PDB.py config_test.json "/allen/aibs/mat/Fahimehb/Data_cube/reobase/Run_folder/result_vmd/dc/perisomatic"
import sys,os
import isee_engine.bionet.config as config
import script.build_3dvis as build_3dvis
import argparse


# args
parser = argparse.ArgumentParser()
parser.add_argument("config_file", help="config file to use as template")
parser.add_argument("output_path", help="out_path")


sargs = parser.parse_args()

config_file = sargs.config_file

out_path = sargs.output_path

conf = config.build(config_file) # Read all the pathes from the manifest 

build_3dvis.CellPDB(conf, out_path)

