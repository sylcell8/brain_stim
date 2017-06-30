import sys
import isee_engine.bionet.params as prm
from isee_engine.bionet import bionet_io
from isee_engine.bionet.network import Network
from isee_engine.bionet.netgraph import NetGraph
from isee_engine.bionet.simulation import Simulation
from isee_engine.bionet.electrode import Electrode


#config_file = str(sys.argv[-1]) # get config file name from the command line argument

config_file = "/data/mat/slg/ice/bionet_sims/120cells/config_test.json"

prm.set_config(config_file)

bionet_io.setup()

ng = NetGraph()                # create a blank graph object
ng.load_internal_nodes()    # load internal model data
net = Network(ng)        # create a NEURON network which includes: cells, connections and external inputs

net.make_cells();      # dictionary for objects of Cell class