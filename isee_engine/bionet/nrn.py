import sys,os
import neuron

from neuron import h
pc = h.ParallelContext()    # object to access MPI methods



def load_neuron_files(conf):
    
    neuron.load_mechanisms(str(conf["manifest"]["$MECHANISMS_DIR"]))

    h.load_file('stdgui.hoc')

    bionet_dir = os.path.dirname(__file__)
    h.load_file(bionet_dir+'/import3d.hoc') # loads hoc files from package directory ./import3d. It is used because read_swc.hoc is modified to suppress some warnings.
    h.load_file(bionet_dir+'/biophysical.hoc')




def quit_execution(): # quit the execution with a message

    pc.done()
    sys.exit()
    
    return


def clear_gids():

    pc.gid_clear()
    pc.barrier()
    


