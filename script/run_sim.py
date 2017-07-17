import sys,os
import isee_engine.bionet.config as config
from isee_engine.bionet import bionet_io,util
from isee_engine.bionet.network import Network
from isee_engine.bionet.graph import Graph
from isee_engine.bionet import nrn
from isee_engine.bionet.simulation import Simulation


def run(config_file_path):
    conf = config.build(config_file_path)  # Read all the pathes from the manifest
    bionet_io.setup_work_dir(conf)  # The working directory, the output and the log files are defined
    graph = Graph(conf)  # create a blank graph object
    nrn.load_neuron_files(conf)  # Load all mechanism and biophysical templates

    net = Network(conf, graph=graph)  # create a network based on graph structure
    net.make_cells()  # instantiate Cells
    net.make_stims()
    net.set_connections()

    sim = Simulation(conf, network=net)  # create an instance of a simulation

    # sim.attach_current_clamp()
    sim.set_recordings()  # set up recordings: Vm, [Ca++], e_extracellular
    sim.set_extra_stimulation()

    sim.run()  # run the simulation

    nrn.quit_execution()


# args = list(sys.argv) # get config file name from the command line argument
# if len(args) > 1: # then assume this is being run as a script
#     print args
    # run(args[-1])