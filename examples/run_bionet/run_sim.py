import sys
import isee_engine.bionet.params as prm
from isee_engine.bionet import bionet_io
from isee_engine.bionet.network import Network
from isee_engine.bionet.netgraph import NetGraph
from isee_engine.bionet.simulation import Simulation
from isee_engine.bionet.electrode import Electrode

#config_file = str(sys.argv[-1]) # get config file name from the command line argument

config_file = "/data/mat/slg/ice/bionet_sims/120cells/config_bckg_lgn.json"


prm.set_config(config_file)

bionet_io.setup()

ng = NetGraph()                # create a blank graph object
ng.load_internal_nodes()    # load internal model data
ng.load_edge_props()
net = Network(ng)        # create a network which includes: cell, connections and external inputs

net.make_cells();      # dictionary for objects of Cell class
net.set_seg_props()
net.set_tar_segs()   # 

net.calc_seg_coords()   # use if need to deal with segment coordinates

external_inputs = ['lgn','background']

for input_name in external_inputs:

    ng.load_external_nodes(input_name)
    net.make_stims(input_name)
    net.set_external_connections(input_name)

#net.set_internal_connections()

mel = Electrode()    # create a multi-electrode to simulate extracellular potential recordings 
sim = Simulation(net,mel)  # create an instance of a simulation  

sim.set_recordings() 
sim.run()